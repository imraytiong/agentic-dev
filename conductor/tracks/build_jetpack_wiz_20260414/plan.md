# Implementation Plan: JetpackWiz Agent

## Layer 1: Data (Models)
- [x] Task: Generate `src/agents/jetpack_wiz/models.py` (Request, State, Response schemas)
- [ ] Task: Conductor - User Manual Verification 'Layer 1: Data'

## Layer 2: Defense (Testing)
- [x] Task: Generate extensive `tests/test_agents/test_jetpack_wiz/test_tools.py`
    - [x] Subtask: Verify surgical clone sequence (blobless -> sparse set -> checkout)
    - [x] Subtask: Verify deep semantic payload construction (10k char per file extraction)
    - [x] Subtask: Verify security guardrails (Path traversal & forbidden git commands)
    - [x] Subtask: Verify context truncation limits (8k for tools, 32k for vector docs)
- [x] Task: Generate `test_agent.py` covering background init and triage loops
- [ ] Task: Conductor - User Manual Verification 'Layer 2: Defense'

## Layer 3: Capabilities (Tools)
- [x] Task: Implement `ensure_repo_and_index` with Deep Semantic Indexing
    - [x] Subtask: Blobless sparse clone logic (`--filter=blob:none --no-checkout`)
    - [x] Subtask: Sparse-checkout configuration (`--no-cone` for README, api/, build.gradle)
    - [x] Subtask: Deep Indexing Loop (Extract 10k chars from each file type per module)
- [x] Task: Implement `resolve_module_path` with semantic search
- [x] Task: Implement `run_git_command` and `read_module_file` with 8k truncation and security scoping
- [ ] Task: Conductor - User Manual Verification 'Layer 3: Capabilities'

## Layer 4: The Brain (Agent)
- [x] Task: Generate `src/agents/jetpack_wiz/agent.py` using `BaseAgentChassis`
    - [x] Subtask: Background init routing with status updates (du -sh and time)
    - [x] Subtask: Proactive notification system and query queuing
    - [x] Subtask: Resilient Triage Loop with self-correction logic
    - [x] Subtask: Version history retrieval using `git tag`
    - [x] Subtask: API change analysis between versions using `git diff` on `current.txt`
- [ ] Task: Conductor - User Manual Verification 'Layer 4: The Brain'

## Layer 5: Configuration & Prompts
- [x] Task: Generate `src/agents/jetpack_wiz/config.yaml` and `prompts/system_prompt.jinja`
- [x] Task: Conductor - User Manual Verification 'Layer 5: Configuration & Prompts'
    - [x] Subtask: Bulleted list formatting for API summaries

## Final Validation
- [x] Task: Run `pytest` and verify local execution with mock infrastructure.
