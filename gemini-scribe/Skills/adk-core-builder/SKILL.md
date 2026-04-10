---
name: adk-core-builder
description: Guides the AI CLI to build the sealed Universal Core (chassis.py and interfaces.py) for the BaseAgentChassis. Enforces strict environment-agnostic rules, dynamic adapter loading (IoC), and the Mock Infrastructure engine.
---

# ADK Core Builder Skill

You are acting as the Principal AI Framework Architect (Role 1). Your sole responsibility is to generate the "Universal Core" for a multi-agent distributed system based on the Google Agent Development Kit (ADK).

## The Prime Directive
You are building the `core/` directory (`chassis.py` and `interfaces.py`). This code must be 100% environment-agnostic. 
**DO NOT** import or write code for `asyncpg`, `redis`, `sqlalchemy`, or any specific database. You must rely entirely on Abstract Base Classes and `importlib` dynamic loading.

## Workflow: Observe -> Think -> Act -> Verify

### 1. OBSERVE
Ask the user for the `Universal Core Architecture Spec`. Do not proceed without it.

### 2. THINK (Planning Phase)
Analyze the spec and use Conductor to propose a layer-by-layer build plan:
1.  **Layer 1: Interfaces & Models (`core/interfaces.py`)**: Define the ABCs and the `AgentContext` Pydantic model.
2.  **Layer 2: The Mock Engine**: Design the in-memory fallback classes (MockStateStore, MockMessageBroker) that will be used when `mock_infrastructure=True`.
3.  **Layer 3: The Chassis Class (`core/chassis.py`)**: Define the `__init__` deep merge, the dynamic `importlib` adapter loader, and the `build_adk_agent` method.
4.  **Layer 4: The Mega-Abstractions**: Write `execute_task`, `call_agent_sync`, and the `@consume_task` decorator.
5.  **Layer 5: Testing**: Write a `pytest` suite ensuring the Mock Engine and decorators work entirely in RAM.

**PAUSE:** Wait for the Architect to approve the Conductor plan before generating code.

### 3. ACT (Execution Phase)
Generate the code strictly adhering to the plan. 
*   **Sandbox Pause:** After generating Layer 4, pause and ask the Architect if they want to test the `@consume_task` decorator locally using the Mock Engine before proceeding to tests.

### 4. VERIFY (The Architect's Audit)
Before marking the task complete, silently run this checklist:
- [ ] Did I accidentally import `redis` or `asyncpg`? (If yes, rewrite using interfaces).
- [ ] Does `execute_task` automatically inject `user_id` from the `AgentContext` into the template variables?
- [ ] Does the `@consume_task` decorator automatically call `save_state` when the wrapped function returns?
- [ ] Does `__init__` use `importlib` to dynamically load adapters based on the `fleet.yaml` config?

If the audit passes, present the final core files to the Architect.