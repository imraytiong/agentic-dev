# Agent Proposal: JetpackWiz 

## 1.0 System Overview
* **1.1 System Objective:** Build an interactive AI agent capable of cloning, navigating, and summarizing the AndroidX/Jetpack monolithic repository. The agent must handle long-running I/O tasks asynchronously, translate human-readable framework concepts into exact repository paths, and strictly manage its context window when analyzing massive code diffs.
* **1.2 Architectural Framework:** The agent must be built upon the `agentic-dev` Hexagonal Architecture framework utilizing Python.

## 2.0 Environment & Storage Strategy
* **2.1 Execution Environment:** The agent will operate uncontainerized, as the deployment environment itself is already a containerized execution space.
* **2.2 Configurable Storage:** The root storage locations for both the target repository clones and the agent's state files MUST be dynamically configurable via the agent's `.yaml` configuration file (no hardcoded absolute paths).
* **2.3 Repository Clone Strategy:** The agent must utilize `git clone --filter=blob:none` combined with `git sparse-checkout` to manage the repository footprint and download times.

## 3.0 State Management Schema
* **3.1 State Storage Mechanism:** The agent must utilize the native memory storage mechanism provided by the `agentic-dev` framework to maintain state, allowing for asynchronous pausing, resuming, and follow-up queries without losing context across sessions.
* **3.2 Active Focus State Object:** The state must track `active_focus`, a JSON object containing the `module_path`, `current_files_in_context`, and `head_sha`.
* **3.3 Command History Array:** The state must track `command_history`, an array of the last 5 executed tool calls to prevent the agent from entering infinite execution loops.
* **3.4 Cached Summaries Ledger:** The state must track `cached_summaries`, a key-value store mapping commit hashes or file paths to LLM-generated summaries. This prevents raw diffs from re-entering the prompt on subsequent conversational turns.
* **3.5 Pending Interrupt State Object:** The state must track `pending_interrupt`, a JSON object storing the agent's mental state and intent when it yields execution to the user for disambiguation.

## 4.0 Tool Specifications
* **4.1 Tool: `resolve_module_path`**
    * **4.1.1 Purpose:** Translates lazy human references (e.g., "Room DB", "Compose UI") into concrete AndroidX directory paths.
    * **4.1.2 Execution Constraint:** The agent MUST call this tool before executing any Git commands if the exact repository path is unknown.
    * **4.1.3 Implementation Directive:** Utilize the `agentic-dev` framework's built-in vector capabilities to embed and perform semantic searches against the parsed `settings.gradle` or directory tree map.
    * **4.1.4 Expected Output:** The tool must return an array of the top 3 to 5 path candidates alongside their confidence scores.
* **4.2 Tool: `run_git_command`**
    * **4.2.1 Purpose:** Safely executes Git commands against the local sparse checkout.
    * **4.2.2 Security and Execution Boundaries:** Raw bash execution is explicitly forbidden. The tool must accept an array of parameterized arguments (e.g., `["log", "-n", "3", "--stat", "--", "path/to/module"]`).
    * **4.2.3 Directory Scoping Guardrail:** The Python function executing the subprocess must force a `cwd` (current working directory) targeted specifically to the configured repository volume.
    * **4.2.4 History Alteration Guardrail:** The tool must block any Git commands that alter remote or local history (e.g., `push`, `reset --hard`).
    * **4.2.5 Auto-Truncation Mechanism:** If the `stdout` of the Git subprocess exceeds 8,000 characters, the tool must automatically truncate the output and return a system warning instructing the agent to use narrower constraints.

## 5.0 Architectural Execution Flows
* **5.1 The Triage Loop**
    * **5.1.1 Prohibited Actions:** The agent is explicitly forbidden from requesting raw unified diffs (`-p`) on large modules without first triaging the blast radius.
    * **5.1.2 Step 1 Initial Discovery:** The agent must run `run_git_command` utilizing the `--stat` or `--name-only` flags.
    * **5.1.3 Step 2 File Review:** The agent reviews the list of changed files from Step 1.
    * **5.1.4 Step 3 Targeted Extraction:** The agent targets a specific, single file to request the raw diff.
* **5.2 The Disambiguation Interrupt**
    * **5.2.1 Trigger Condition:** If the `resolve_module_path` tool returns multiple low-confidence candidates, the agent must trigger an interrupt.
    * **5.2.2 Step 1 State Preservation:** The agent saves its current intent and the list of options to the `pending_interrupt` state.
    * **5.2.3 Step 2 User Prompting:** The agent outputs the options to the user and completely yields execution.
    * **5.2.4 Step 3 State Rehydration:** Upon receiving the user's reply, the framework rehydrates the agent's state, injects the selected path, and resumes execution.

## 6.0 Implementation Tasks for the AI Assistant
* **6.1 Interrupt Hooking Task:** Review the `BaseAgentChassis` in the `agentic-dev` core. Determine how to implement the `YieldToUser` interrupt pattern within the existing event loop.
* **6.2 Mock Injection Task:** Structure the `run_git_command` tool so it can seamlessly read from local mock fixtures during unit testing instead of invoking the actual `subprocess.run`.
* **6.3 Post-Clone Indexing Task:** Write a post-clone hook script that extracts the AndroidX directory map and loads it into the framework's vector store to power the `resolve_module_path` tool.