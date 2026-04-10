# Hackathon Execution Strategy: Building the Agent Fleet

This document outlines how a team can effectively collaborate to build the foundational architecture and first working agents using Agent-Driven Development (AI CLIs).

## 1. The Trilateral Team Structure (Division of Labor)

To move at hackathon speed, developers cannot step on each other's toes. Because we abstracted the architecture into a "Core vs. Adapters" model, we cleanly divide the work into three distinct roles.

### Role 1: The Architect (Ray - Technical Director)
*   **The Mission:** Own the "Universal Core" and direct the overall system contracts.
*   **Focus Areas:**
    *   **The Core:** Maintains the sealed `core/chassis.py` and `core/interfaces.py`. Ensures the core remains pristine and environment-agnostic.
    *   **Contract Enforcement:** Finalizes the **Pydantic Models** (`models.py`) that agents use to talk to each other. The AI CLI is *never* allowed to change these without your approval.
    *   **Strategic Direction:** Maintains the Architectural Decision Log and resolves any disputes between Infra and App devs.

### Role 2: The Infrastructure Leads (Platform Engineers)
*   **The Mission:** Connect the sealed Universal Core to the real-world operational environment.
*   **Focus Areas:**
    *   **Building Adapters:** Use the AI CLI (`adk-infra-builder`) to write the specific `asyncpg` (Postgres) and message broker connection adapters inside the `adapters/` folder.
    *   **Environment Mapping:** Map specific environment constraints (Colima on Mac vs. Podman on Corp Linux) to the deployment configurations.
    *   **Deployment Manifests:** Generate the `docker-compose.yml`, `fleet.yaml`, `Dockerfile`, and configure Arize Phoenix.
*   **Success Metric:** The Docker network spins up cleanly, and the mock chassis can be swapped to `mock_infrastructure=False` without breaking agent logic.

### Role 3: The Agent Developers (App Engineers)
*   **The Mission:** Build the actual "Doers" (e.g., The Deep Researcher or Supervisor) that provide functional value.
*   **Focus Areas:**
    *   **Business Logic:** Writing the specific `tools.py` and configuring the `config.yaml` for each agent.
    *   **The Brain:** Writing the Jinja prompts and defining the agent personas.
    *   **Wiring:** Using the AI CLI (`adk-agent-builder`) to wire up `agent.py` using the Chassis decorators.
*   **Success Metric:** The agent successfully executes its logic loop, uses a tool, and saves its final state. *They use `mock_infrastructure=True` on Day 1 to avoid being blocked by the Infra Leads.*

---

## 2. The Hackathon Timeline (Day-by-Day)

### Day 1: The "Mock" Milestone
*   **Goal:** A fully working system, entirely in RAM.
*   **Action:** The Architect provides the Universal Core. Agent Developers use `mock_infrastructure=True`. No Docker, no Postgres. Agent Developer's Supervisor talks to Worker agents using Python queues.
*   **Why:** Proves the agent logic and Pydantic contracts work before adding infrastructure headaches.

### Day 2: The "Plumbing" Milestone
*   **Goal:** Swap RAM for real infrastructure.
*   **Action:** Infrastructure Leads finish the `docker-compose.yml` and the Postgres/Broker adapters. The team sets `mock_infrastructure=False`. The agents now talk via real brokers and save to real databases.

### Day 3: The "Skill" Milestone
*   **Goal:** Make the agents smart.
*   **Action:** Focus shifts entirely to `tools.py` and `prompts/`. The plumbing works; now the Agent Developers use the AI CLI to rapidly generate new tools (web scrapers, SQL generators) and test the agents' reasoning loops.