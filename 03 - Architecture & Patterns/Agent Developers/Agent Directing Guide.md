---
links:
  - "[Agentic Coding Playbook](Agentic%20Coding%20Playbook.md)"
  - "[Developer Guide](Developer%20Guide.md)"
tags:
  - agentic-coding
  - gemini-cli
  - conductor
  - workflow
  - multi-agent-systems
---
# Agent Directing Guide: Gemini CLI & Conductor

**Tags:** #agentic-coding #gemini-cli #conductor #workflow
**Status:** Active Reference

Welcome to the Director's chair. You are not a typist; you are a Technical Director managing an autonomous coding agent. 

This guide assumes you are using **Gemini CLI** paired with **Conductor** (the planning tool), and that you are already familiar with the fundamental **Observe -> Think -> Act -> Verify** loop of directing agents. 

Here is how you apply that loop specifically to build agents within our `BaseAgentChassis` architecture.

---

## 1. OBSERVE: Setting the Boundaries (The Skill)
An AI coding agent is eager to please. If you give it a blank canvas, it will hallucinate raw SQL or SQLAlchemy boilerplate. 

Instead of manually prompting the AI with all of our architectural rules, we have codified our entire framework into a reusable **Skill**.

**Your Action:**
Before opening Conductor or writing any code, load the custom skill into your CLI:
1. Command your CLI to load the **[adk-agent-builder](../../08%20-%20AI%20CLI%20Skills/adk-agent-builder.md)** skill.
2. Feed the CLI the specific **[Agent Architecture Spec](../../06%20-%20Templates/Agent%20Architecture%20Spec.md)** for the agent you are building (or use the skill's interactive brain-dump mode to generate one!).

**What the Skill Does:**
You no longer need to write massive explicit prompts. The skill automatically forces the AI to read the **[BaseAgentChassis Reference](../Platform%20Engineers/BaseAgentChassis%20Reference.md)**, forbids it from writing raw infrastructure code, and mandates the use of our decorators (`@chassis.consume_task`) and security contexts.

---

## 2. THINK: The Conductor Planning Phase
Do not let the AI start writing code immediately. Use Conductor to generate a step-by-step implementation plan. 

**Your Action:**
Ask Conductor to draft the plan. Because you loaded the `adk-agent-builder` skill, the AI is already programmed to break the work down into our mandated "Layers". **Review the plan to ensure it followed the skill instructions:**

*   **Step 1: The Contract (`models.py`).** Define the Pydantic schemas for the REST payloads and JSONB state.
*   **Step 2: The Defense (`test_models.py` & `test_tools.py`).** Write the pytest suite *before* the logic.
*   **Step 3: The Hands (`tools.py`).** Write the standard Python functions.
*   **Step 4: The Brain (`agent.py`).** Wire up the `@chassis.consume_task` decorator and business logic.
*   **Step 5: The Config (`config.yaml` & `prompts/`).** Externalize the settings and Jinja instructions.

*Director's Note: If the AI strays and suggests writing `agent.py` first, reject the plan and remind it of the skill's layer-by-layer rule.*

---

## 3. Directing Multi-Agent Systems (MAS)
If your goal is to build a "Society of Minds" (e.g., a Supervisor and two Workers), **do not ask the AI to build the entire fleet in one prompt.** The AI will get overwhelmed and tangle the logic.

**Your Action:**
1. Give the AI your overarching MAS brain dump.
2. The `adk-agent-builder` skill is programmed to automatically **Halt and Divide**. It will help you identify the distinct agents needed.
3. **Lock the Inter-Agent Contracts:** Before building *any* agent, work with the CLI to define the Pydantic models that will be passed between them (e.g., the JSON payload the Supervisor sends to the Worker).
4. **Build One by One:** Pick the first agent (usually the Supervisor or a core Worker), generate its specific `Agent Architecture Spec`, and run it through the Layer-by-Layer execution. Once Agent A is finished, restart the process for Agent B.

---

## 4. ACT: Layer-by-Layer Execution & The Sandbox Pause
Once the Conductor plan is approved, you transition to the Gemini CLI execution phase. 

**Your Action:**
Let the CLI execute the plan one step at a time. Do not walk away from the keyboard. Watch the terminal as it generates the code. 

**The Sandbox Pause (Interactive Testing):**
The `adk-agent-builder` skill is programmed to **pause** after generating Layer 3 (`tools.py`) and Layer 4 (`agent.py`). 
Instead of blindly rushing to the next step, the CLI will ask you: *"Would you like to pause and test this layer in isolation?"*
*   *Director's Move:* Say **Yes**. The CLI will generate a temporary `test_run.py` script or use the `chassis.run_local(mock_infrastructure=True)` method so you can interact with the tool or the agent's brain right there in your terminal. Play with it, verify the prompt tone, and test edge cases. Once you are satisfied, tell the CLI to resume the plan.

**The TDD Defense Mechanism:**
When the CLI runs tests, if it gets stuck in a loop trying to fix a failing test, pause the execution.
*   *Director's Move:* Read the error. Sometimes the AI wrote a bad test, not bad code. Guide the CLI: *"The code is fine, but you forgot to mock the `chassis.execute_task` method in the pytest. Fix the test."*

---

## 5. VERIFY: The Architectural Sanity Check
The CLI just reported "Task Complete." The code looks clean, and the tests pass. **Do not trust it blindly.** While the skill includes self-correction rules, AI agents can still make subtle regressions.

**Your Action:**
Perform the Director's Code Review. Look specifically for these common hallucinations:

### ❌ The Hallucination Checklist:
- [ ] **Did it hardcode the model?** Check `agent.py`. It should *not* say `model="gemini-1.5-pro"`. It should rely on `chassis.config`.
- [ ] **Did it write raw network requests?** Check `tools.py` and `agent.py`. It should *not* import `httpx` for inter-agent communication. It must use `await chassis.call_agent_sync()`.
- [ ] **Did it forget the Security Context?** Check the chassis method calls. Every call to `execute_task`, `publish_async_task`, or `save_state` *must* pass the `context: AgentContext` object.
- [ ] **Did it hardcode the prompt?** Check `agent.py`. There should be no massive multi-line text strings. It must use `template="system.jinja"`.

### ✅ The Final Verification:
Run the local mock test.
```bash
python agent.py
```
If `chassis.run_local(mock_infrastructure=True)` executes perfectly in your terminal, the agent is ready for the Docker/K3s cluster. You have successfully directed the AI.

---
## Progressive Learning Path
If you are new to this architecture, we recommend reading these guides in the following order:
1. **[Conceptual Guide - What is an Agent](Conceptual%20Guide%20-%20What%20is%20an%20Agent.md):** Start here to understand the high-level theory without the code.
2. **[Developer Guide](Developer%20Guide.md):** Move here to see the actual Python code and the 5-step workflow.
3. **[Agent Directing Guide](Agent%20Directing%20Guide.md):** Read this when you are ready to use Gemini CLI to actually generate the code.
4. **[Agentic Coding Playbook](Agentic%20Coding%20Playbook.md):** The meta-rules for team collaboration and architecture defense.

---
## 6. The MAS Threshold: When to Split an Agent

Knowing exactly *when* to break a single agent into a Multi-Agent System (MAS) is the hallmark of a great Director. Do not split agents prematurely (which adds unnecessary network latency), but do not wait until a "God Agent" collapses under its own weight.

Watch for these **Four Thresholds**. If your agent crosses any of them, it is time to split:

### Threshold 1: The "Schizophrenic Persona"
*   **The Symptom:** Your system prompt starts containing conflicting instructions like: *"Be highly creative and brainstorm wildly, but also be strictly analytical, adhere to PEP-8, and never output invalid JSON."*
*   **The Split:** Create the **Debate Pattern**. Split it into a Creative Drafter Agent and a Ruthless Critic Agent. Let them argue; don't force one brain to do both.

### Threshold 2: The "Tool Overload"
*   **The Symptom:** Your agent has more than 5-7 complex tools attached to it (e.g., `search_web`, `query_postgres`, `read_s3`, `send_email`, `trigger_pagerduty`). The agent starts hallucinating tool arguments or using the wrong tool for the job.
*   **The Split:** Create the **Manager & Specialist Pattern**. Build a Supervisor Agent whose *only* tool is `delegate_task`. Build a Data Agent that only has the `query_postgres` tool, and a Comms Agent that only has the `send_email` tool.

### Threshold 3: The "Speed vs. Brains" Conflict
*   **The Symptom:** You have a fast, high-volume task (like sorting 1,000 incoming emails) mixed with a slow, high-reasoning task (like drafting a complex technical response to 5 of them). If you use `gemini-1.5-pro` for everything, it's too slow and expensive. If you use `gemini-1.5-flash`, the technical responses are poor.
*   **The Split:** Create the **Factory Line Pattern**. Use a tiny, fast agent to sort the queue, and pass the hard ones to a massive, slow agent.

### Threshold 4: The "Context Window Blowout"
*   **The Symptom:** The agent needs to read 50 massive PDFs to answer a question. If you try to stuff all 50 PDFs into one prompt, the LLM hits its token limit or suffers from "Lost in the Middle" syndrome (forgetting the middle of the text).
*   **The Split:** Create the **Map-Reduce Pattern**. Spin up 50 "Worker Agents" that each read exactly one PDF and extract the facts. Send those 50 tiny summaries to one "Synthesizer Agent" to write the final report.