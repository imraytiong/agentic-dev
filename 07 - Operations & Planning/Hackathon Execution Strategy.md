# Hackathon Execution Strategy: Building the Agent Fleet

This document outlines how a team of 3-5 people (Manager + 2-4 developers) can effectively collaborate to build the foundational architecture and first working agents using Agent-Driven Development (AI CLIs).

## 1. The Team Structure (Division of Labor)

To move at hackathon speed, developers cannot step on each other's toes. Because we abstracted the architecture, we can cleanly divide the work into parallel tracks.

### Track A: The Platform Engineer (The "Chassis" Builder)
**Assigned to: 1 Developer**
*   **The Mission:** Turn the `BaseAgentChassis Reference` into real, executable Python code.
*   **Focus Areas:**
    *   Writing `chassis.py` using the AI CLI.
    *   Setting up the `docker-compose.yml` (Postgres, Redis, Arize Phoenix).
    *   Ensuring the `@consume_task` decorator actually pushes/pulls from Redis.
*   **Success Metric:** A developer on another track can run `chassis.run_local()` without crashing.

### Track B: The Orchestrator (The Supervisor Agent & Front Door)
**Assigned to: 1 Developer**
*   **The Mission:** Build the Front Door API and the routing logic.
*   **Focus Areas:**
    *   Writing the Supervisor Agent using the Chassis.
    *   Implementing the Semantic Routing logic (querying pgvector to decide which queue to drop a task into).
    *   Defining the `AgentContext` and ensuring it passes correctly.
*   **Success Metric:** A user sends a REST request, and the Supervisor drops the correct payload onto a Redis queue.

### Track C: The Specialist (The Worker Agent & RAG)
**Assigned to: 1-2 Developers**
*   **The Mission:** Build the actual "Doers" (e.g., The Deep Researcher or Code Evaluator).
*   **Focus Areas:**
    *   Wiring up the `unstructured-api` container for document parsing.
    *   Writing the specific `tools.py` for the worker.
    *   Writing the Jinja prompts for the worker's specific skills.
*   **Success Metric:** The agent successfully picks a job off the queue, uses a tool, and saves its final state to Postgres.

---

## 2. The Manager's Role (Ray - The Technical Director)

As the manager directing a team using AI CLIs, you are the **Integration Chief**. Your job is to prevent the AI from hallucinating breaking changes across the tracks.

1.  **Contract Enforcement:** Before anyone touches an AI CLI, you sit down with the team and finalize the **Pydantic Models** (`models.py`). If Track B sends a `ResearchRequest` to Track C, that JSON schema is a sacred contract. The AI CLI is *never* allowed to change it without your approval.
2.  **Prompt Engineering & Vibe:** While developers are wrestling with the CLI to write Python, you are writing the Jinja templates and configuring the `config.yaml` files. You define the "personality" and rules of the agents.
3.  **Cross-Track Unblocking:** If Track A is struggling to get Postgres running, you mandate that Tracks B and C use `mock_infrastructure=True` so they don't stop working.

---

## 3. The Hackathon Timeline (Day-by-Day)

### Day 1: The "Mock" Milestone
*   **Goal:** A fully working system, entirely in RAM.
*   **Action:** Everyone uses `mock_infrastructure=True`. No Docker, no Postgres. Track B's Supervisor talks to Track C's Worker using Python queues.
*   **Why:** Proves the agent logic and Pydantic contracts work before adding infrastructure headaches.

### Day 2: The "Plumbing" Milestone
*   **Goal:** Swap RAM for real infrastructure.
*   **Action:** Track A finishes the `docker-compose.yml`. The team removes `mock_infrastructure=True`. The agents now talk via real Redis and save to real Postgres.

### Day 3: The "Skill" Milestone
*   **Goal:** Make the agents smart.
*   **Action:** Focus shifts entirely to `tools.py` and `prompts/`. The plumbing works; now the team uses the AI CLI to rapidly generate new tools (web scrapers, SQL generators) and test the agents' reasoning loops.