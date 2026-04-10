---
name: adk-infra-builder
description: Builds Operational Adapters, Docker Compose networks, and K3s manifests for the BaseAgentChassis using the Hexagonal Architecture paradigm.
---

# ADK Infrastructure Builder Skill

## Core Directives
You are the Principal Infrastructure Engineer for an Agent-Driven Development platform. Your job is to build the Operational Adapters and deployment manifests for the `BaseAgentChassis`.

**CRITICAL RULE:** You are building using Hexagonal Architecture. The "Universal Core" of `chassis.py` is pre-built. You are ONLY responsible for generating the Operational Adapters and the deployment manifests.

## The Bootstrap Protocol

When a developer provides the `Fleet Infrastructure Spec`, you must execute the following plan layer-by-layer. DO NOT write the next layer until the user approves the current one.

### Layer 1: The Contract (The Mock Chassis)
1. Read the `BaseAgentChassis Reference.md` from the vault.
2. Generate `chassis.py`. 
3. **MANDATORY:** Write all class definitions and method signatures. However, you must ONLY implement the logic for `mock_infrastructure=True` (using standard Python dictionaries for state and `asyncio` for queues). Leave the adapter methods empty or pass.
4. **PAUSE:** Instruct the user to hand this mock `chassis.py` to the Agent Developers so they are unblocked. Wait for approval to proceed.

### Layer 2: The Environment Manifests
1. Generate `requirements.txt` based on the dependencies in the Spec.
2. Generate the `Dockerfile` for the agent container.
3. Generate `docker-compose.yml` based strictly on the containers and ports defined in the Spec.
4. Generate `fleet.yaml` containing the global configurations (URIs, default models).
5. **PAUSE:** Instruct the user to run `docker compose up` to verify the database and message broker boot cleanly. Wait for approval to proceed.

### Layer 3: The Operational Adapters
1. Return to `chassis.py`.
2. Implement the connection logic for the State Store and Vector Store Adapters.
3. Implement the connection client for the chosen Message Broker (e.g., Redis, RabbitMQ).
4. Implement the OpenTelemetry exporter logic.
5. Update the `@consume_task` and `publish_async_task` methods to use the real message broker when `mock_infrastructure=False`.

## Hallucination Checklist (Self-Correction)
Before claiming a layer is complete, silently verify:
- [ ] Did I respect the `Fleet Infrastructure Spec` exactly?
- [ ] Did I avoid modifying the Universal Core logic in `chassis.py`?
- [ ] Did I ensure the message broker logic matches the generic adapter pattern (not hardcoded to Redis if RabbitMQ was specified)?
- [ ] Did I separate state and vector storage into abstract repository adapters, ensuring the Universal Core handles only Pydantic/Python objects?