# 2. Agent Builder Playbook

**Tags:** #agentic-coding #playbook #team-workflow #ai-cli
**Status:** Active Reference

Welcome to the practice phase. In this vault, human engineers act as **Technical Directors**. We write strict specifications, provide constrained context, and direct AI Coding Agents (Antigravity CLI, Gemini CLI, Cursor) to generate the actual Python code.

This playbook outlines exactly how to build and test an agent safely within the `BaseAgentChassis` architecture.

---

## 1. The "Mock First" Paradigm

You do **not** need to wait for the Infrastructure Leads to finish setting up Docker, Postgres, or Redis. You can start generating brains immediately!
By using `chassis.run_local(mock_infrastructure=True)`, your agent will use in-memory dictionaries and queues. Once the Infra team is ready, you simply turn off the mock and your agent connects to the real databases without rewriting a single line of business logic.

---

## 2. The 4 Rules of Directing Coding Agents

AI coding agents are eager to please and will invent infrastructure if you don't restrict them.

### Rule 1: Feed the Contract (Context Scoping)
Whenever you instruct an AI to create a new agent, you **must** load the `adk-agent-builder` skill. 
*   **Action:** Fire up your CLI and type `load adk-agent-builder`.
*   **Why:** It forces the AI to read the BaseAgentChassis rules, forbids raw infrastructure code, and mandates the use of our decorators.

### Rule 2: Generate in Layers (The Step-by-Step Workflow)
Do not ask an AI CLI to "Build the Research Agent." Direct it layer by layer:
1.  **Layer 1 (Data):** Generate `models.py` for Pydantic schemas and JSONB state.
2.  **Layer 2 (Defense):** Write the `test_models.py` & `test_tools.py` pytest suite *before* the logic.
3.  **Layer 3 (The Hands):** Generate `tools.py` with standard async Python functions.
4.  **Layer 4 (The Brain):** Generate `agent.py` using the `@chassis.consume_task` decorator.
5.  **Layer 5 (Config):** Externalize settings to `config.yaml` and instructions to `prompts/`.

### Rule 3: Test-Driven Defense (TDD)
Before asking the AI to write complex business logic, ask it to write the `pytest` file first. Once the test is locked in, the AI CLI is forced to generate code that passes it.

### Rule 4: Lock Down Integration Points
Pydantic models that define inter-agent communication must be treated as sacred contracts. If Team A is building the Supervisor and Team B is building the Worker, lock the Pydantic schemas first.

---

## 3. The Execution Loop: Observe -> Think -> Act -> Verify

### A. OBSERVE
*   Grab the **[Agent Spec Template](../../spec_templates/agent_spec_template.md)**, fill out your business logic, and hand it to the CLI.

### B. THINK (The Conductor Planning Phase)
*   Ask Conductor (or your CLI) to draft the step-by-step implementation plan. 
*   Ensure it follows the "Generate in Layers" rule. Reject the plan if it tries to write `agent.py` first.

### C. ACT (The Sandbox Pause)
*   Let the CLI execute the plan one step at a time.
*   **The Sandbox Pause:** After generating the tools or the agent brain, pause the execution. The CLI will generate a temporary `test_run.py` script. Play with it in your terminal, verify the prompt tone, and test edge cases before resuming.

### D. VERIFY (The Hallucination Checklist)
Do not trust the final code blindly. Look for these common AI hallucinations:
- [ ] **Did it hardcode the model?** It should rely on `chassis.config`, not `model="gemini-1.5-pro"`.
- [ ] **Did it write raw network requests?** It must use `await chassis.call_agent_sync()`, not `httpx` for inter-agent communication.
- [ ] **Did it forget the Security Context?** Every chassis method *must* pass the `context: AgentContext` object.
- [ ] **Did it hardcode the prompt?** It must use `template="system.jinja"`, not massive text strings in Python.

---

## 4. Testing Your Agents (The Out-of-the-Box Experience)

Our `BaseAgentChassis` provides an incredible "out-of-the-box" testing experience without requiring you to build a custom frontend. Both natively support **Multimodal inputs (File Uploads & Links)**.

### A. The "Agent Studio" (Local Web UI)
When you run `python agent.py` with `mock_infrastructure=True`, the Chassis automatically spins up an embedded web application.
1. Run `python agent.py`
2. Open your browser to `http://localhost:8000/studio`
3. **Multimodal Testing:** Click the paperclip icon in the UI to drop PDFs, code files, or paste links. The FastAPI backend automatically passes the content directly into the ADK state for the LLM!

### B. The IDE Integration (MCP Server)
The ultimate "cheat code" for testing is the **Model Context Protocol (MCP)**.
1. Run `python agent.py`.
2. Open an MCP-compatible IDE like **Cursor** or **Windsurf**.
3. Add a new MCP Server pointing to `http://localhost:8000/mcp/sse`.
4. **Files & Links:** Highlight code in your IDE, use `@Files` to attach PDFs, or paste a link. The IDE reads the file context and streams it securely to the agent over MCP!

### C. Sending Files Back to the User (Outbound Multimodal)
If your agent generates a report or modifies an image:
1. **The Tool:** Use the Chassis adapter (e.g., `chassis.file_storage.save_file(data)`) to save it and return a `file_id`.
2. **The Response:** The agent outputs a Markdown link: `[Download Report](/download/12345)`.
3. **The Clients:**
   - **Agent Studio:** Renders the link as a clickable download button.
   - **MCP (IDE):** Allows the user to click and save the file directly into their workspace.

---

## 5. Deployment

When you are done testing logic locally:

**Fleet Orchestration (Docker Compose)**
```bash
docker compose up --build research_agent
```
*The agent is now running as a microservice, listening for REST calls and consuming from Redis.*

**Production Deployment (K3s)**
Because the Chassis adheres to OCI container standards and exposes standard `/health` endpoints, deploying requires zero code changes.
```bash
kubectl apply -f k8s/research-agent-deployment.yaml
```