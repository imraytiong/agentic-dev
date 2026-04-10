# Hackathon Execution Strategy: Building the Agent Fleet

This document outlines how a team of 3-5 people (Manager + 2-4 developers) can effectively collaborate to build the foundational architecture and first working agents using Agent-Driven Development (AI CLIs).

## 1. The Team Structure (Division of Labor)

To move at hackathon speed, developers cannot step on each other's toes. Because we abstracted the architecture into a "Core vs. Adapters" model, we can cleanly divide the work into parallel tracks.

### Track A: The Platform Engineer (Adapters & Infrastructure)
**Assigned to: 1 Developer**
*   **The Mission:** Connect the pre-built "Universal Core" of the Chassis to the real-world operational environment.
*   **Focus Areas:**
    *   **The Immediate Handoff:** Ensure the Universal Core (with `mock_infrastructure=True`) is immediately available to Tracks B & C.
    *   **Building Adapters:** Use the AI CLI to write the specific `asyncpg` (Postgres) and `redis` connection adapters inside `chassis.py`.
    *   **Deployment Manifests:** Generate the `docker-compose.yml`, `Dockerfile`, and configure Arize Phoenix.
*   **Success Metric:** The Docker network spins up cleanly, and the mock chassis can be swapped to `mock_infrastructure=False` without breaking agent logic.

### Track B: The Orchestrator (The Supervisor Agent & Front Door)
**Assigned to: 1 Developer**
*   **The Mission:** Build the Front Door API and the routing logic.
*   **Focus Areas:**
    *   Writing the Supervisor Agent using the pre-built Core Chassis.
    *   Implementing the Semantic Routing logic (querying pgvector to decide which queue to drop a task into).
    *   Defining the `AgentContext` and ensuring it passes correctly.
*   **Success Metric:** A user sends a REST request, and the Supervisor drops the correct payload onto a dummy Redis queue using the mock infrastructure.

### Track C: The Specialist (The Worker Agent & RAG)
**Assigned to: 1-2 Developers**
*   **The Mission:** Build the actual "Doers" (e.g., The Deep Researcher or Code Evaluator).
*   **Focus Areas:**
    *   Wiring up the `unstructured-api` container for document parsing.
    *   Writing the specific `tools.py` for the worker.
    *   Writing the Jinja prompts for the worker's specific skills.
*   **Success Metric:** The agent successfully executes its logic loop, uses a tool, and saves its final state to the mock Postgres dictionary.

---

## 2. The Manager's Role (Ray - The Technical Director)

As the manager directing a team using AI CLIs, you are the **Integration Chief**. Your job is to prevent the AI from hallucinating breaking changes across the tracks.

1.  **Contract Enforcement:** Before anyone touches an AI CLI, you sit down with the team and finalize the **Pydantic Models** (`models.py`). If Track B sends a `ResearchRequest` to Track C, that JSON schema is a sacred contract. The AI CLI is *never* allowed to change it without your approval.
2.  **Prompt Engineering & Vibe:** While developers are wrestling with the CLI to write Python, you are writing the Jinja templates and configuring the `config.yaml` files. You define the "personality" and rules of the agents.
3.  **Cross-Track Unblocking:** You ensure Tracks B and C use `mock_infrastructure=True` on Day 1 so they are never blocked waiting for Track A's Docker network to stabilize.

---

## 3. The Hackathon Timeline (Day-by-Day)

### Day 1: The "Mock" Milestone
*   **Goal:** A fully working system, entirely in RAM.
*   **Action:** Track A hands over the Universal Core. Tracks B & C use `mock_infrastructure=True`. No Docker, no Postgres. Track B's Supervisor talks to Track C's Worker using Python queues.
*   **Why:** Proves the agent logic and Pydantic contracts work before adding infrastructure headaches.

### Day 2: The "Plumbing" Milestone
*   **Goal:** Swap RAM for real infrastructure.
*   **Action:** Track A finishes the `docker-compose.yml` and the Postgres/Redis adapters. The team sets `mock_infrastructure=False`. The agents now talk via real Redis and save to real Postgres.

### Day 3: The "Skill" Milestone
*   **Goal:** Make the agents smart.
*   **Action:** Focus shifts entirely to `tools.py` and `prompts/`. The plumbing works; now the team uses the AI CLI to rapidly generate new tools (web scrapers, SQL generators) and test the agents' reasoning loops.