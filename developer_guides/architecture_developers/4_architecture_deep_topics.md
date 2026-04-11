# 4. Deep Topics (Advanced Reading)

**Status:** Post-Hackathon / Homework
**Target Audience:** Architecture Developers maintaining the Universal Core.

This guide explores the theoretical evolution of the Universal Core and advanced orchestration patterns. It is meant for deep architectural discussions, not day-one hackathon building.

## 1. The Actor Model Evolution

Currently, our `BaseAgentChassis` uses a task-based queue system (Redis). As the system scales, you may want to evolve it into a pure Actor Model (using frameworks like Ray or Akka).
*   **Why:** In an Actor Model, each agent instance is a stateful actor living in memory, rather than pulling state from Postgres on every request.
*   **How:** This would require a major refactor of the `chassis.py` to handle mailbox routing and supervisor hierarchies, moving away from the stateless FastAPI worker paradigm.

## 2. Dynamic Agent Registries & Discovery

Right now, if Agent A wants to talk to Agent B, it drops a message in a known Redis queue. In a massive enterprise, agents need to discover each other dynamically.
*   **The Registry:** Implement a central "Yellow Pages" interface (`BaseAgentRegistry`).
*   **The Flow:** Agent A queries the registry: *"I need an agent that knows how to query SAP."* The registry returns the routing key for the SAP Agent.
*   **Implementation:** This requires adding a new Port to `interfaces.py` and building an adapter (e.g., using Consul or etcd).

## 3. Advanced Security Context Propagation

When an agent executes a tool on behalf of a user, it needs to prove it has permission.
*   **Zero-Trust Execution:** The Universal Core must extract the standard JWT or SAML token from the initial FastAPI request.
*   **Context Passing:** That token must be securely serialized into the Redis task payload.
*   **Execution:** When a tool makes an outbound API call, the Chassis automatically injects that user's token into the Authorization header, ensuring the agent cannot bypass internal IAM policies.