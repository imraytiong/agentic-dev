import pytest
import unittest
import os
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock, call
from src.agents.jetpack_wiz.tools import run_git_command, resolve_module_path, read_module_file, ensure_repo_and_index

@pytest.mark.asyncio
async def test_resolve_module_path_semantic_search():
    # Mocking a vector store
    mock_vector_store = MagicMock()
    mock_vector_store.semantic_search = AsyncMock(return_value=[
        MagicMock(metadata={"path": "compose/ui"}, score=0.95),
        MagicMock(metadata={"path": "compose/runtime"}, score=0.85)
    ])
    
    results = await resolve_module_path("Compose UI", mock_vector_store)
    assert len(results) == 2
    assert results[0]['path'] == "compose/ui"
    assert results[0]['score'] == 0.95

@pytest.mark.asyncio
@patch("src.agents.jetpack_wiz.tools.subprocess.run")
async def test_run_git_command_security_and_scoping(mock_run):
    mock_run.return_value = MagicMock(stdout="commit abc", stderr="", returncode=0)
    
    # 1. Test Scoping
    await run_git_command(["log", "-n", "1"], repo_path="/tmp/androidx")
    mock_run.assert_called_with(["git", "log", "-n", "1"], cwd="/tmp/androidx", capture_output=True, text=True, check=False)
    
    # 2. Test Forbidden Commands
    with pytest.raises(ValueError, match="Forbidden Git command"):
        await run_git_command(["push", "origin"], repo_path="/tmp/androidx")
    with pytest.raises(ValueError, match="Forbidden Git command"):
        await run_git_command(["reset", "--hard"], repo_path="/tmp/androidx")

@pytest.mark.asyncio
@patch("src.agents.jetpack_wiz.tools.subprocess.run")
async def test_run_git_command_8k_truncation(mock_run):
    large_output = "a" * 10000
    mock_run.return_value = MagicMock(stdout=large_output, stderr="", returncode=0)
    
    result = await run_git_command(["log"], repo_path="/tmp/androidx")
    assert len(result) <= 8500
    assert "SYSTEM WARNING: Output truncated" in result

@pytest.mark.asyncio
@patch("src.agents.jetpack_wiz.tools.os.path.exists", return_value=True)
async def test_read_module_file_guardrails(mock_exists):
    repo_path = "/tmp/androidx"
    
    # 1. Test Path Traversal Protection
    result = await read_module_file("../../../etc/passwd", repo_path)
    assert "ERROR: Access denied" in result
    
    # 2. Test 8k Truncation
    large_content = "b" * 10000
    with patch("builtins.open", unittest.mock.mock_open(read_data=large_content)):
        result = await read_module_file("api/current.txt", repo_path)
        assert len(result) <= 8500
        assert "SYSTEM WARNING: File content truncated" in result

@pytest.mark.asyncio
@patch("src.agents.jetpack_wiz.tools.subprocess.run")
@patch("src.agents.jetpack_wiz.tools.os.path.exists")
@patch("src.agents.jetpack_wiz.tools.os.makedirs")
async def test_ensure_repo_and_index_clone_sequence(mock_makedirs, mock_exists, mock_run):
    # Setup: Repo doesn't exist
    mock_exists.side_effect = lambda p: False if ".git" in p else True
    mock_run.return_value = MagicMock(stdout="compose/ui\nroom/room-compiler", returncode=0)
    mock_vector_store = MagicMock()
    mock_vector_store.add_documents = AsyncMock()

    # We need to mock open for the indexing phase within the same test
    with patch("builtins.open", unittest.mock.mock_open(read_data="fake content")):
        await ensure_repo_and_index("/tmp/androidx", mock_vector_store)

    # Verify the specific surgical clone commands
    expected_calls = [
        call(["git", "clone", "--filter=blob:none", "--no-checkout", "https://android.googlesource.com/platform/frameworks/support", "."], cwd="/tmp/androidx", check=True),
        call(["git", "sparse-checkout", "set", "--no-cone", "/*", "**/README.md", "**/api/current.txt", "**/build.gradle", "**/build.gradle.kts"], cwd="/tmp/androidx", check=True),
        call(["git", "checkout", "HEAD"], cwd="/tmp/androidx", check=True),
        call(["git", "ls-tree", "-d", "-r", "--name-only", "HEAD"], cwd="/tmp/androidx", capture_output=True, text=True, check=True)
    ]
    mock_run.assert_has_calls(expected_calls, any_order=False)

@pytest.mark.asyncio
@patch("src.agents.jetpack_wiz.tools.subprocess.run")
@patch("src.agents.jetpack_wiz.tools.os.path.exists", return_value=True)
async def test_ensure_repo_and_index_deep_indexing_logic(mock_exists, mock_run):
    # Setup: Mock 1 directory found
    mock_run.return_value = MagicMock(stdout="compose/ui", returncode=0)
    mock_vector_store = MagicMock()
    mock_vector_store.add_documents = AsyncMock()
    
    # Mock reading 12k chars from README (simulating > 10k limit)
    very_large_content = "X" * 12000
    
    with patch("builtins.open", unittest.mock.mock_open(read_data=very_large_content)) as mock_open:
        await ensure_repo_and_index("/tmp/androidx", mock_vector_store)
        
        # Verify it tried to read the expected files
        # (It should check for README.md, build.gradle, etc.)
        mock_open.assert_any_call(os.path.abspath("/tmp/androidx/compose/ui/README.md"), 'r')
        
        # Verify the document added to vector store is rich but capped at 32k (and files capped at 10k)
        args, kwargs = mock_vector_store.add_documents.call_args
        doc = kwargs.get('documents')[0] # First document in batch
        
        assert "Path: compose/ui" in doc
        assert "--- README ---" in doc
        # Ensure the 'X' block for README was truncated to 10k, not 12k
        # Combined with headers, the 'X' sequence shouldn't be 12000 long
        assert "X" * 10001 not in doc
        assert len(doc) <= 32000
