# Implementation Plan: Base Agent Chassis

## Phase 1: Foundation (Domain Interfaces)
- [x] Task: Create `src/universal_core/interfaces.py` with all ABCs (07f3205)
- [x] Task: Define `AgentContext` and generic type variables (07f3205)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation (Domain Interfaces)' (Protocol in workflow.md)

## Phase 2: The Universal Chassis (Dependency Injection & Lifecycle)
- [x] Task: Implement `BaseAgentChassis.__init__` with config merging (eababc0)
- [x] Task: Implement dynamic infrastructure loading logic via `importlib` (eababc0)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: The Universal Chassis' (Protocol in workflow.md)

## Phase 3: Service Layer & Mega-Abstractions
- [x] Task: Implement `ask_structured` with Pydantic retry loop (adb5c5e)
- [x] Task: Implement `execute_task` with Jinja2 template injection (adb5c5e)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Service Layer & Mega-Abstractions' (Protocol in workflow.md)

## Phase 4: Communication & Event Handling (Decorators & API)
- [~] Task: Implement `@consume_task` decorator for message polling
- [x] Task: Implement FastAPI endpoints for file upload/download and MCP SSE (adb5c5e)
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Communication & Event Handling' (Protocol in workflow.md)

## Phase 5: Developer Experience & Validation (Mock Engine & Agent Studio)
- [~] Task: Implement mock adapters for all interfaces
- [x] Task: Implement `run_local()` and the embedded Agent Studio UI (adb5c5e)
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Developer Experience & Validation' (Protocol in workflow.md)