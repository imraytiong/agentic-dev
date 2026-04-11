# 2. Architecture Playbook (The Practice)

**Target Audience:** The Architect (Role 1)
**Goal:** A tactical guide to using the AI CLI to build the Universal Core.

---

## 1. OBSERVE: The Setup
Do not let the AI guess what a chassis is. You must constrain it strictly to our design.

**Your Action:**
1. Open your Gemini CLI (or preferred AI coding assistant).
2. Activate the skill: `load adk-core-builder` (view the skill instructions in `skills/adk-core-builder/SKILL.md`).
3. The CLI will initialize and ask for the spec. Feed it the **Universal Core Architecture Spec** located at `src/universal_core/universal_core_architecture_spec.md`.

## 2. THINK: The Conductor Plan
Instruct the CLI: *"Use Conductor to map out the execution plan based on the skill instructions and the spec."*

**The Architect's Review:**
When Conductor presents the plan, verify it follows this exact sequence. If it deviates, reject the plan.
*   **Layer 1: The Contracts (`interfaces.py`).** It must define the Abstract Base Classes (`BaseStateStore`, `BaseMCPServer`, etc.) first.
*   **Layer 2: The Core Object (`chassis.py` - Init).** It must write the `__init__` method, the `config.yaml` deep merge, and the `importlib` dynamic loading.
*   **Layer 3: The Mega-Abstractions.** It must write `execute_task`, `ask_structured`, and `call_agent_sync`.
*   **Layer 4: The Decorators & UI.** It must write `@consume_task`, `@with_retry`, and wire up the FastAPI routes for the Agent Studio and MCP.
*   **Layer 5: The Mock Engine.** It must implement the `run_local(mock_infrastructure=True)` logic.

## 3. ACT: Execution & The Sandbox Pause
Tell the CLI to execute the plan. Watch the terminal closely.

When the CLI finishes Layer 5, tell it to pause. 
*   *Your Move:* Ask the CLI to generate a quick `test_core.py` script that uses `mock_infrastructure=True` and a dummy agent function.
*   Run `python test_core.py` in your terminal. 
*   Does the `@consume_task` decorator successfully pull a fake payload from the queue? Can you access the `/studio` UI?
*   If yes, the core is solid.

## 4. VERIFY: The Golden Sanity Check
Before you seal the core and hand it to your team, you must perform a strict audit. AI tools love to sneak helpful (but illegal) imports into base classes.

### 🚨 The Architect's Hallucination Checklist:
- [ ] **The Prime Directive:** Open `src/universal_core/chassis.py`. Search for `import redis`, `import asyncpg`, or `import sqlalchemy`. If *any* of those exist, the AI hallucinated. Delete them and instruct the AI to use the interfaces.
- [ ] **True Inversion of Control:** Verify that the infrastructure clients (`self.state_store_client`, etc.) are instantiated using `importlib` based on strings from the config, NOT hardcoded imports.
- [ ] **UI & MCP:** Verify the `GET /mcp/sse` and `GET /studio` routes exist.
- [ ] **Context Injection:** Check the `execute_task` method. Did the AI automatically inject `context.user_id` into the Jinja template variables?
- [ ] **Pydantic Enforcement:** Check the `@consume_task` decorator. Does it strictly require a `state_model: Type[BaseModel]`?