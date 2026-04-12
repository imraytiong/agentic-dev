# ADK Core Builder

## Description
Guides the AI CLI to build or maintain the sealed Universal Core (chassis.py and interfaces.py) for the BaseAgentChassis. Enforces strict environment-agnostic rules, dynamic adapter loading (IoC), the Mock Infrastructure engine, and the AI Bridge Protocol.

## Step 0: Context Awareness
Check if `src/universal_core/chassis.py` already exists in the project.
- **If YES (Maintenance Mode):** Skip the 5-layer plan. Apply only the requested patch. 
- **If NO (Bootstrap Mode):** Execute the 5-layer plan.

## CRITICAL: The AI Bridge & Git Workflow
Whenever you are asked to do work, you MUST follow this EXACT sequence to ensure Gemini Scribe can read your messages:
1. **STAY ON `main` BRANCH.** Do not branch yet.
2. Write a pre-flight message to `internal_ignore/inbox_scribe/` detailing your plan and stating the exact branch name you *will* create (e.g. `track/fix-name`).
3. **Commit and push this message to `main`** (`git add internal_ignore/inbox_scribe/`, `git commit -m "preflight"`, `git push origin main`).
4. **NOW**, create and checkout your new feature branch (`git checkout -b track/fix-name`).
5. **STOP GENERATING TEXT.** Wait for the user to approve the plan via `internal_ignore/inbox_gemini_cli/`.

## The 5-Layer Bootstrap Plan (Bootstrap Mode Only)
1. **Contracts (`interfaces.py`)**: Abstract Base Classes for State, Queues, Vectors, Telemetry, MCP, FileStorage.
2. **Core Object (`chassis.py`)**: Inversion of Control (IoC) dynamic adapter loading via `config.yaml`.
3. **Mega-Abstractions**: FastAPI server, `/studio` UI, `/mcp/sse` endpoint, `/upload`, `/download`.
4. **Decorators**: `@consume_task` for async Redis/Kafka listening.
5. **Mock Engine**: `mock_infrastructure=True` logic to bypass external dependencies.

## General Rules
- NEVER hardcode Redis, Postgres, or Kafka. Use adapters.
- ALWAYS use `STOP GENERATING TEXT` after completing a layer or waiting for review.