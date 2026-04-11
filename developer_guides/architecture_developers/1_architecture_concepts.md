# 1. Architecture Concepts (The Theory)

**Target Audience:** The Architect (Role 1)
**Goal:** Understand the philosophy and boundaries of the Universal Core before building it.

As the Architect, your job is to build the foundation of the entire system before the hackathon even begins (or in the very first hour). You are building the `src/universal_core/` directory. This code must be pristine, heavily typed, and completely isolated from the real world via the Abstract Repository Pattern.

## The Universal Core (`BaseAgentChassis`)

The Universal Core is the beating heart of all agents in the fleet. It is a sealed, environment-agnostic Python library (`chassis.py` and `interfaces.py`). 

Its primary responsibility is to heavily abstract away the boilerplate of running an AI agent, allowing Agent Developers to focus solely on business logic.

### Core Principles:
1. **Environment Agnostic:** The core must never know if it is running on a Mac Mini or a K3s cluster. It must not contain hardcoded imports for external databases or message queues (no `import redis` or `import asyncpg`).
2. **Strict Contracts:** It communicates with the outside world purely through Abstract Base Classes (defined in `interfaces.py`). 
3. **Inversion of Control (IoC):** The core dynamically loads infrastructure adapters at runtime based on string paths provided in the `config.yaml`.

## The Hackathon Handoff

The Architect's role is front-loaded. Your timeline looks like this:

1. **Hour 1:** Use the AI CLI to generate the Universal Core.
2. **Hour 2:** Perform the Golden Sanity Check to ensure the AI didn't hallucinate illegal imports.
3. **The Handoff:** Lock the `src/universal_core/` folder. Hand the interfaces to the **Infrastructure Leads** (so they can build adapters) and hand the chassis to the **Agent Developers** (so they can start building brains using `mock_infrastructure=True`).
4. **The Rest of the Event:** Transition into the role of Integration Chief—reviewing Pydantic contracts and writing Jinja prompts.