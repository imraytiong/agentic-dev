# Agent Fleet Deployment Infrastructure

**Tags:** #architecture #deployment #docker #docker-compose #k3s #adk #distributed
**Status:** Baseline Established

## Strategic Decision: Distributed-First (Cloud-Agnostic & Lightweight)
We have deliberately chosen a **Distributed-First** approach over a monolithic application. Each agent in our fleet operates as an independent microservice. Furthermore, to avoid vendor lock-in and support both a local Mac Mini and small Linux clusters, we are prioritizing **lightweight, cloud-agnostic containerization**.

### Why Distributed?
1. **Blast Radius Containment:** AI agents can be unpredictable. If one agent encounters an Out-Of-Memory (OOM) error due to a massive context window or gets stuck in a recursive tool-calling loop, it will only crash its own container, leaving the rest of the fleet unaffected.
2. **Resource Asymmetry:** A `RouterAgent` needs high concurrency and low latency. A `DataAnalysisAgent` running local pandas/embeddings needs heavy CPU/RAM. Distributing allows us to scale and provision hardware specifically for each agent's needs.
3. **Dependency Isolation:** Agent A might require an older specific version of a library for a tool, while Agent B needs the newest version. Containerization prevents dependency hell.

---

## 1. The `BaseAgentChassis` (Shared Plumbing)
To ensure that building a new agent doesn't require rewriting networking and lifecycle code, we will construct a shared Python library component: the `BaseAgentChassis`.

When you write a new agent, it inherits from this chassis.
The chassis automatically handles:
- Wrapping the ADK agent in a FastAPI application.
- Standardized `asynccontextmanager` lifespans (startup/shutdown).
- Injecting standard `/health` and `/ready` probes.
- Bootstrapping OpenTelemetry tracing.
- Connecting to the centralized State/Memory database.

**Developer Experience:** You only write the Prompts, Tools, and ADK configuration. The chassis makes it a deployable Docker microservice.

---

## 2. Orchestration & Infrastructure Concepts

Since our primary targets are a dedicated Mac Mini and small-team Linux environments, we reject heavy cloud-managed services (like Vertex AI) and bloated Kubernetes distributions (like GKE/EKS). 

We will use a two-phased approach:

### Phase 1: Local & Single-Node (Docker Compose)
For the Mac Mini and initial development, **Docker Compose** is our orchestrator.
- **Simplicity:** A single `docker-compose.yml` file spins up the entire fleet (agents, PostgreSQL memory, Redis/RabbitMQ).
- **Internal Networking:** Docker automatically handles internal DNS. The `RouterAgent` simply calls `http://research-agent:8000`.
- **Lightweight:** Minimal overhead on the Mac Mini compared to running a local Kubernetes cluster.

### Phase 2: Small Work Environment (K3s or Docker Swarm)
When moving to a containerized Linux cluster for a small team, we will use **K3s** (Lightweight Kubernetes by Rancher) or **Docker Swarm**.
- **K3s:** A fully compliant Kubernetes distribution packaged as a single binary. It uses a fraction of the memory of standard K8s, making it perfect for bare-metal Linux servers while still giving us powerful features like Horizontal Pod Autoscaling (HPA) and self-healing.
- **Portability:** Because our `BaseAgentChassis` standardizes the `/health` checks and container format, moving from Docker Compose to K3s requires zero code changes to the agents themselves.

---

## 3. Inter-Agent Communication Patterns

In a distributed cluster, agents must talk to each other over the network. We will support two patterns within our system:

1. **Synchronous (REST/gRPC):** 
   - *Use Case:* Fast, immediate answers. (e.g., A user asks a question, the Router Agent queries the RAG Agent and waits for the answer to stream back).
   - *Tech:* Handled natively by ADK's HTTP endpoints and Docker's internal DNS.
2. **Asynchronous (Event-Driven / Queues):**
   - *Use Case:* Long-running tasks. (e.g., The Router Agent asks the Research Agent to "Read these 50 PDFs and summarize them"). We don't want HTTP timeouts.
   - *Tech:* **Lightweight Message Brokers** (like Redis Pub/Sub or RabbitMQ). The Router Agent drops a task on a queue, immediately replies to the user "I'm working on it," and the Research Agent picks up the task from the queue when it has capacity. No dependency on heavy cloud brokers like Google Pub/Sub.

---

## Next Steps
1. Draft the Python skeleton for the `BaseAgentChassis`.
2. Create a baseline `docker-compose.yml` that includes our core infrastructure (Postgres, Redis) and a dummy agent.