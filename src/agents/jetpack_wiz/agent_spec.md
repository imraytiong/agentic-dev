# Agent Architecture Spec: JetpackWiz

## 1. Meta Information
*   **Agent Name:** JetpackWiz
*   **Location:** `src/agents/jetpack_wiz/`
*   **Queue Name:** `@chassis.consume_task(queue_name="jetpack_wiz_jobs")`
*   **Model:** Omit from code; allow `BaseAgentChassis` to use the `fleet.yaml` default.
*   **Testing:** Write an extensive `pytest` suite in `tests/test_agents/test_jetpack_wiz/`.
*   **Capabilities:** Module Discovery, Git Analysis, API Surface Review, Version History.

## 2. Models (`models.py`)
*   **Payload Model (`JetpackWizRequest`):**
    *   `query: str`: The user's natural language command.
    *   `user_reply: Optional[str]`: The user's response to a pending interrupt.
*   **Response Model (`JetpackWizResponse`):**
    *   `message: str`: The final response or interrupt prompt to the user.
    *   `is_interrupt: bool`: Flag indicating if the agent yielded for disambiguation.
*   **State Model (`JetpackWizState`):**
    *   `status: str = "initialized"`
    *   `is_cloning: bool = False`: Tracks background clone status.
    *   `is_indexing: bool = False`: Tracks background directory indexing status.
    *   `has_indexed: bool = False`: Tracks if indexing completed successfully for the session.
    *   `clone_start_time: Optional[float]`: Timestamp of when cloning began.
    *   `pending_notifications: List[str]`: Queue of proactive messages.
    *   `pending_queries: List[str]`: Queue of user queries received during background init.
    *   `active_focus: ActiveFocus`: Pydantic object tracking `module_path`, `current_files_in_context`, and `head_sha`.
    *   `command_history: List[str]`: Array of the last 5 executed commands.
    *   `cached_summaries: Dict[str, str]`: Ledger of LLM-generated summaries.
    *   `pending_interrupt: Optional[PendingInterrupt]`: Tracks `intent`, `options`, and `original_request`.

## 3. Tools (`tools.py`)
*   **`ensure_repo_and_index(repo_path: str, vector_store: Any) -> str`**:
    *   **Phase 1 (Clone):** Performs a blobless clone (`--filter=blob:none --no-checkout`).
    *   **Phase 2 (Sparse-Checkout):** Configures patterns for "/*", "**/README.md", "**/api/current.txt", "**/build.gradle", and "**/build.gradle.kts" using `--no-cone`. Runs `git checkout HEAD` to download contents.
    *   **Phase 3 (Deep Indexing):** Recursively iterates through all modules found via `git ls-tree`.
        *   **Extraction:** Reads the first **10,000 characters** of each module's README, build script, and public API file.
        *   **Concatenation:** Combines them into a single searchable document (labeled by section).
        *   **Limit:** Truncates the final combined document at **32,000 characters** before storing in the vector database.
*   **`resolve_module_path(query: str, vector_store: Any) -> List[Dict[str, Any]]`**:
    *   Performs semantic search against the deep index. Returns top candidates and confidence scores.
*   **`run_git_command(args: List[str], repo_path: str) -> str`**:
    *   Safely executes Git commands against the local checkout via `subprocess.run`.
    *   **Guardrails:** Forced `cwd` scoping, explicit blocks on history-altering commands, and output truncation at **8,000 characters**.
*   **`read_module_file(file_path: str, repo_path: str) -> str`**:
    *   Safely reads files within the repo.
    *   **Guardrails:** Prevents path traversal and truncates at **8,000 characters**.

## 4. Agent Logic (`agent.py`)
*   **Execution Flow:**
    1.  **Background Init:** If the repo isn't ready, trigger `ensure_repo_and_index` in the background. Queue incoming queries. Report `du -sh` and elapsed time.
    2.  **Proactive Analysis:** Once indexing finishes, process every query in the `pending_queries` queue sequentially and store results in `pending_notifications`.
    3.  **Conversational Catch:** Intercept status pings or help requests when the repo is ready but no module is selected.
    4.  **Resilient Triage Loop:** Uses `execute_task` to get LLM decisions. If a git command fails, the agent inspects the error and is allowed one self-correction retry via `run_git` before summarizing for the user.
    5.  **Version Analysis:** If the user asks for versions, the agent finds the artifact prefix in `build.gradle` and uses `git tag` to list the top 5 releases.

## 5. Configuration (`config.yaml` & `prompts/system.jinja`)
*   **Config:** Store `repo_path` dynamically.
*   **System Prompt:** 
    *   Strict Rule: No raw diffs without `--stat`.
    *   Strict Rule: Always use `--` separator for paths in git commands.
    *   Strict Rule: Never provide meta-commentary/apologies for tool failures.
    *   Capability Suggestion: Remind the user about the ability to analyze API surfaces via `current.txt`.
    *   API Summary: ALWAYS format public API summaries as a clean, bulleted list of classes/functions.
