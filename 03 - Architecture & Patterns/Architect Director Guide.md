---
tags:
  - architect
  - director-guide
  - core
  - gemini-cli
status: Active
---
# Architect Director Guide: Building the Universal Core

**Target Audience:** The Architect (Role 1)
**Goal:** Using Gemini CLI + Conductor to build the sealed, environment-agnostic `BaseAgentChassis` (The Universal Core).

As the Architect, your job is to build the foundation of the entire system before the hackathon even begins (or in the very first hour). You are building the `core/` directory. This code must be pristine, heavily typed, and completely isolated from the real world via the Abstract Repository Pattern.

---

## 1. OBSERVE: The Setup
Do not let the AI guess what a chassis is. You must constrain it strictly to our design.

**Your Action:**
1. Open your Gemini CLI.
2. Type: `load adk-core-builder`
3. The CLI will initialize and ask for the spec. Copy the contents of `[[Universal Core Architecture Spec]]` (from the `06 - Templates` folder) and paste it into the prompt.

## 2. THINK: The Conductor Plan
Instruct the CLI: *"Use Conductor to map out the execution plan based on the skill instructions and the spec."*

**The Architect's Review:**
When Conductor presents the plan, verify it follows this exact sequence. If it deviates, reject the plan.
*   **Layer 1: The Contracts (`core/interfaces.py`).** It must define the Abstract Base Classes (`BaseStateStore`, etc.) first.
*   **Layer 2: The Core Object (`core/chassis.py` - Init).** It must write the `__init__` method, the `config.yaml` deep merge, and the `importlib` dynamic loading.
*   **Layer 3: The Mega-Abstractions.** It must write `execute_task`, `ask_structured`, and `call_agent_sync`.
*   **Layer 4: The Decorators.** It must write `@consume_task` and `@with_retry`.
*   **Layer 5: The Mock Engine.** It must implement the `run_local(mock_infrastructure=True)` logic.

## 3. ACT: Execution & The Sandbox
Tell the CLI to execute the plan. Watch the terminal closely.

**The Mock Engine Sandbox Pause:**
When the CLI finishes Layer 5, tell it to pause. 
*   *Your Move:* Ask the CLI to generate a quick `test_core.py` script that uses `mock_infrastructure=True` and a dummy agent function.
*   Run `python test_core.py` in your terminal. 
*   Does the `@consume_task` decorator successfully pull a fake payload from the `asyncio` queue? Does it save the state to the in-memory Python dictionary? 
*   If yes, the core is solid.

## 4. VERIFY: The Golden Sanity Check
Before you seal the core and hand it to your team, you must perform a strict audit. AI CLIs love to sneak helpful (but illegal) imports into base classes.

### 🚨 The Architect's Hallucination Checklist:
- [ ] **The Prime Directive:** Open `core/chassis.py`. Search for `import redis`, `import asyncpg`, or `import sqlalchemy`. If *any* of those exist, the AI hallucinated. Delete them and instruct the AI to use the interfaces.
- [ ] **True Inversion of Control:** Verify that the infrastructure clients (`self.state_store_client`, etc.) are being instantiated using `importlib` based on strings from the config, NOT hardcoded imports.
- [ ] **Context Injection:** Check the `execute_task` method. Did the AI automatically inject `context.user_id` and `context.session_id` into the Jinja template variables?
- [ ] **Pydantic Enforcement:** Check the `@consume_task` decorator. Does it strictly require a `state_model: Type[BaseModel]`?

## 5. The Hackathon Handoff
Once the `core/` directory passes the Golden Sanity Check, your job as the primary coder is done. 

1. Zip the `core/` directory.
2. Hand it to **Track A (Infrastructure Leads)**. Tell them: *"Here is the Universal Core. Do not modify it. Build the adapters in the `adapters/` folder to satisfy `core/interfaces.py`."*
3. Hand it to **Tracks B & C (Agent Developers)**. Tell them: *"Here is the Chassis. Use `mock_infrastructure=True` and start building your agents immediately."*
4. Transition into your role as **Integration Chief**—reviewing Pydantic contracts and writing Jinja prompts.
