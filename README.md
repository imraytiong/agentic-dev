# AI Agent Engineering Framework & Vault

Welcome to the **Agent Engineering Vault**, the central strategic and operational repository for building distributed AI agents using the Google Agent Development Kit (ADK) and Python.

This repository is designed specifically for **Agent-Driven Development**. It contains not only the architecture for the microservices we build but also the strict rules, playbooks, and AI CLI skills required to direct AI coding assistants (like Gemini CLI or Antigravity) to build them safely.

## 🏗 Architecture Overview

We employ a **Distributed-First Microservice Architecture** (Hexagonal Architecture) to ensure maximum scalability, fault tolerance, and separation of concerns.

*   **Framework:** Google Agent Development Kit (ADK), strictly Python.
*   **The Spine (Universal Core):** The `BaseAgentChassis`—a shared, sealed Python library that wraps all agents in FastAPI, handles OpenTelemetry, and manages health probes.
*   **Async Communication:** Redis (or generic Message Broker) for long-running queues.
*   **Sync Communication:** REST + strict Pydantic JSON payloads.
*   **State & Memory:** PostgreSQL + `pgvector` (Segregated tables for Conversational Memory and Document Knowledge, with JSONB for flexible Agent State).
*   **Observability:** OpenTelemetry natively routed to Arize Phoenix.
*   **Deployment:** OCI-compliant containers running on Colima (Mac) or Podman/K3s (Linux).

## 👥 Trilateral Team Structure

To prevent AI coding assistants from hallucinating across boundaries and causing merge conflicts, this framework enforces a strict division of labor:

1.  **The Architect (Role 1):** Owns the sealed `core/` directory (`BaseAgentChassis`), defines the Pydantic contracts, and maintains the strategic vision.
2.  **Platform Engineers (Role 2):** Focus exclusively on the `adapters/` directory, `fleet.yaml`, and mapping the environment (Docker/Podman/K3s).
3.  **Agent Developers (Role 3):** Focus exclusively on building functional value (`agent.py`, `tools.py`, `prompts/`).

## 🚀 Quick Start & Entry Points

Depending on your role, start by reading your specific guides in the vault:

*   **[Vault Dashboard](00%20-%20Dashboard.md)** - The central hub for all active agent projects and documentation.
*   **[Agent Developers: Start Here](02%20-%20Architecture%20&%20Patterns/Agent%20Developers/00%20-%20Start%20Here.md)** - Learn how to write business logic, prompts, and tools without worrying about infrastructure.
*   **[Platform Engineers: Director Guide](02%20-%20Architecture%20&%20Patterns/Platform%20Engineers/Infrastructure%20Director%20Guide.md)** - Learn the Bootstrap Protocol for generating the operational adapters and deployment manifests.
*   **[Architect: Director Guide](02%20-%20Architecture%20&%20Patterns/Architect%20Director%20Guide.md)** - Learn how to build and maintain the sealed Universal Core.

## 🤖 AI CLI Skills

This repository includes pre-programmed instructions (Skills) for your AI CLI. These skills enforce our architectural guardrails during code generation. You can find them in the `07 - AI CLI Skills/` directory:

*   `adk-agent-builder.md`: For Agent Developers.
*   `adk-infra-builder.md`: For Platform Engineers.
*   `adk-core-builder.md`: For the Architect.

To use them, simply load the markdown file into your CLI of choice before generating code.

---
*Status: Hackathon Ready*