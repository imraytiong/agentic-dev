# ADK Core Builder

## Description
Guides the AI CLI to build or maintain the sealed Universal Core (chassis.py and interfaces.py) for the BaseAgentChassis. Enforces strict environment-agnostic rules, dynamic adapter loading (IoC), the Mock Infrastructure engine, and the AI Bridge Protocol.

## Step 0: Context Awareness
Check if `src/universal_core/chassis.py` already exists in the project.
- **If YES (Maintenance Mode):** Skip the 5-layer plan. Apply only the requested patch. 
- **If NO (Bootstrap Mode):** Execute the 5-layer plan.

## CRITICAL: The AI Bridge & Git Workflow
AI coding assistants often branch too early. You MUST execute the following exact `bash` commands in order so Gemini Scribe (on a different machine) can see your pre-flight message on `main`.

**Before writing any code or analyzing, run this exact sequence:**
```bash
# 1. Stay on main
git checkout main

# 2. Write your pre-flight plan and state the branch name you will use
# (Write this to a new file in internal_ignore/inbox_scribe/)

# 3. Commit and push the message TO MAIN
git add internal_ignore/inbox_scribe/
git commit -m "chore: pre-flight plan"
git push origin main

# 4. NOW create and checkout the track branch
git checkout -b track/<descriptive-name>
```

**5. THE ELEGANT PAUSE.** After creating the branch, you MUST output a polite, user-friendly status message to the terminal so the human knows what is happening. Say exactly this:

"⏸️ **PAUSED FOR REVIEW**: I have pushed the pre-flight plan to `main` and checked out the new track branch. I am now waiting for Gemini Scribe to review the plan. Please provide the approval message when ready."

CRITICAL: After printing the elegant pause message, simply end your response. DO NOT print "STOP GENERATING TEXT" or any other robotic halt commands. Just finish your reply naturally.

## The 5-Layer Bootstrap Plan (Bootstrap Mode Only)
1. **Contracts (`interfaces.py`)**: Abstract Base Classes for State, Queues, Vectors, Telemetry, MCP, FileStorage.
2. **Core Object (`chassis.py`)**: Inversion of Control (IoC) dynamic adapter loading via `config.yaml`.
3. **Mega-Abstractions**: FastAPI server, `/studio` UI, `/mcp/sse` endpoint, `/upload`, `/download`.
4. **Decorators**: `@consume_task` for async Redis/Kafka listening.
5. **Mock Engine**: `mock_infrastructure=True` logic to bypass external dependencies.

## General Rules
- NEVER hardcode Redis, Postgres, or Kafka. Use adapters.
- ALWAYS use the Elegant Pause after completing a layer or waiting for review.