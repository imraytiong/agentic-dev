# Specification: Base Agent Chassis

## Overview
This track implements the core orchestration engine for the AI Agent Engineering Framework, following a Hexagonal Architecture.

## Architecture Reference
The implementation must adhere to:
- `src/universal_core/universal_core_architecture_spec.md`
- `internal_ignore/inbox_scribe/01_chassis_plan.md` (Approved 5-Layer Plan)

## Core Requirements
1. **Pristine Core:** 100% environment-agnostic with no infrastructure-specific imports.
2. **Dynamic Loading:** Infrastructure loaded via `importlib` and `fleet.yaml`.
3. **Mega-Abstractions:** Simplified `execute_task` and `ask_structured` methods with built-in JSON healing.
4. **Multimodal Support:** Native FastAPI multipart handling.
5. **Local Harness:** Mock engine and Agent Studio UI for zero-dependency development.