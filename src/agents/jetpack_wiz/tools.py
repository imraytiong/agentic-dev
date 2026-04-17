import subprocess
import os
import asyncio
import uuid
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

async def ensure_repo_and_index(repo_path: str, vector_store: Any) -> str:
    """
    Ensures the AndroidX repository is cloned using a blobless sparse strategy 
    and its directory structure + metadata is deeply indexed into the vector store.
    """
    status_messages = []
    repo_url = "https://android.googlesource.com/platform/frameworks/support"
    
    # PHASE 1: Surgical Clone (Blobless + No-Checkout)
    if not os.path.exists(os.path.join(repo_path, ".git")):
        os.makedirs(repo_path, exist_ok=True)
        logger.info(f"🚀 CLONE START: Surgical blobless clone into {repo_path}...")
        status_messages.append(f"Cloning AndroidX (blobless) into {repo_path}...")
        
        # 1.1 Initial blobless clone with no checkout to keep footprint tiny
        await asyncio.to_thread(
            subprocess.run,
            ["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, "."],
            cwd=repo_path,
            check=True
        )
        
        # 1.2 Configure sparse-checkout for metadata files only
        await asyncio.to_thread(
            subprocess.run,
            ["git", "sparse-checkout", "set", "--no-cone", "/*", "**/README.md", "**/api/current.txt", "**/build.gradle", "**/build.gradle.kts"],
            cwd=repo_path,
            check=True
        )
        
        # 1.3 Checkout the metadata blobs
        await asyncio.to_thread(
            subprocess.run,
            ["git", "checkout", "HEAD"],
            cwd=repo_path,
            check=True
        )
        
        logger.info("✅ CLONE COMPLETE.")
        status_messages.append("Clone complete.")
    
    # PHASE 2: Deep Semantic Indexing
    if hasattr(vector_store, "add_documents"):
        logger.info("📂 INDEX START: Deep semantic mapping of directory structure...")
        status_messages.append("Deep indexing metadata into vector store...")
        
        try:
            # Get list of all module directories from git index (depth limited to 2-3 levels)
            result = await asyncio.to_thread(
                subprocess.run,
                ["git", "ls-tree", "-d", "-r", "--name-only", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            directories = [d.strip() for d in result.stdout.split("\n") if d.strip()]
            
            # Filter for likely module roots (depth 1 or 2)
            module_paths = [d for d in directories if d.count("/") <= 2]
            
            documents = []
            metadatas = []
            ids = []
            
            for path in module_paths:
                # Build rich semantic payload (Extract 10k chars from each file type)
                parts = [f"Path: {path}"]
                
                # Helper to read and format sections
                for filename, label in [("README.md", "README"), ("build.gradle", "BUILD SCRIPT"), ("build.gradle.kts", "BUILD SCRIPT"), ("api/current.txt", "PUBLIC API")]:
                    full_file_path = os.path.join(repo_path, path, filename)
                    if os.path.exists(full_file_path):
                        try:
                            with open(full_file_path, 'r') as f:
                                # Extract 10,000 characters per requirements
                                content = f.read(10000)
                                parts.append(f"--- {label} ---\n{content}")
                        except Exception:
                            pass
                
                # Combine and cap total document at 32,000 characters
                full_doc = "\n\n".join(parts)
                if len(full_doc) > 32000:
                    full_doc = full_doc[:31900] + "\n\n[TRUNCATED]"
                
                documents.append(full_doc)
                metadatas.append({"path": path})
                ids.append(uuid.uuid4().hex)
                
                # Batch processing every 100 modules for memory efficiency
                if len(documents) >= 100:
                    await vector_store.add_documents(documents=documents, metadatas=metadatas, ids=ids)
                    documents, metadatas, ids = [], [], []

            # Final batch
            if documents:
                await vector_store.add_documents(documents=documents, metadatas=metadatas, ids=ids)
            
            logger.info(f"✅ INDEX COMPLETE: Indexed {len(module_paths)} modules with deep semantic data.")
            status_messages.append(f"Indexed {len(module_paths)} directories.")
                
        except Exception as e:
             logger.error(f"❌ INDEX FAILURE: {e}")
             status_messages.append(f"Error during indexing: {e}")
             
    return "\n".join(status_messages)

async def resolve_module_path(query: str, vector_store: Any) -> List[Dict[str, Any]]:
    """
    Translates lazy human references into concrete AndroidX directory paths.
    Utilizes semantic search against the deep metadata index.
    """
    if hasattr(vector_store, "semantic_search"):
        results = await vector_store.semantic_search(query, limit=5)
        return [{"path": r.metadata.get("path", str(r)), "score": getattr(r, 'score', 0.0)} for r in results]
    elif hasattr(vector_store, "search"):
        return vector_store.search(query)
    
    return []

async def run_git_command(args: List[str], repo_path: str) -> str:
    """
    Safely executes Git commands against the local sparse checkout.
    - Parameterized arguments to prevent shell injection.
    - Forced directory scoping to the repo_path.
    - Blocking history-altering commands.
    - Auto-truncation of output at 8,000 characters.
    """
    forbidden_cmds = {"push", "reset", "rebase", "commit", "merge"}
    if any(cmd in args for cmd in forbidden_cmds):
        raise ValueError(f"Forbidden Git command detected in arguments.")

    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        output = result.stdout if result.returncode == 0 else f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            
        if len(output) > 8000:
            output = output[:8000] + "\n\n... [SYSTEM WARNING: Output truncated to 8000 characters. Use narrower constraints.]"
            
        return output
    except Exception as e:
        return f"CRITICAL ERROR executing git command: {str(e)}"

async def read_module_file(file_path: str, repo_path: str) -> str:
    """
    Safely reads a file from the repository.
    - Ensures the path is within the repo_path.
    - Auto-truncation at 8,000 characters.
    """
    full_path = os.path.abspath(os.path.join(repo_path, file_path))
    if not full_path.startswith(os.path.abspath(repo_path)):
        return "ERROR: Access denied. Path is outside the repository scope."
    
    if not os.path.exists(full_path):
        return f"ERROR: File not found at {file_path}"
    
    try:
        with open(full_path, 'r') as f:
            content = f.read(8001)
            
        if len(content) > 8000:
            content = content[:8000] + "\n\n... [SYSTEM WARNING: File content truncated to 8000 characters.]"
            
        return content
    except Exception as e:
        return f"ERROR reading file: {str(e)}"
