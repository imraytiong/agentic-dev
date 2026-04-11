# 1. Infrastructure Concepts (The Theory)

**Target Audience:** Infrastructure Leads / Platform Engineers
**Goal:** Understand the Hexagonal Architecture and the "Open Core" model that powers the agent fleet.

While the Agent Developers are building the "Brains", your job is to build the "Spine" of the system. 

We use a **Hexagonal Architecture (Ports and Adapters)** approach with **True Inversion of Control (IoC)**. You are *not* building the `BaseAgentChassis` from scratch. The "Universal Core" (`src/universal_core/chassis.py`) is sealed, pre-built, and strictly owned by the Architect. Your job is to build the **Operational Adapters** in the `src/infrastructure/` directory that connect that core to the real world.

## Why We Use Adapters (The "Open Core" Model)
Adapters allow our Universal Core to remain completely agnostic to the environment it runs in. This is crucial for our dual-remote setup: we can use standard open-source tools on our local machines, but instantly swap to proprietary corporate systems during the hackathon *without changing a single line of the core agent code*. You just update the YAML config!

```mermaid
flowchart LR
    subgraph "🛡️ Universal Core (Sealed)"
        Chassis["BaseAgentChassis"] -->|Defines Needs| Port["interfaces.py<br/>(e.g., BaseMessageQueue)"]
    end

    subgraph "🔌 Infrastructure Layer (Adapters)"
        Port -.->|Public Config| Redis["public_adapters/ <br/> RedisAdapter"]
        Port -.->|Corporate Config| Kafka["internal_adapters/ <br/> CorpKafkaAdapter"]
    end

    subgraph "🌍 External Systems"
        Redis --> LiveRedis[("(Standard Redis)")]
        Kafka --> LiveKafka[("(Secure Corp Kafka)")]
    end
    
    style Chassis fill:#2d3748,stroke:#4fd1c5,color:#fff
    style Port fill:#2d3748,stroke:#fc8181,color:#fff
    style Redis fill:#2b6cb0,stroke:#63b3ed,color:#fff
    style Kafka fill:#805ad5,stroke:#b794f4,color:#fff
    style LiveRedis fill:#4a5568,color:#fff
    style LiveKafka fill:#4a5568,color:#fff
```

## The Dual Remote Git Strategy
Because we are building proprietary adapters during a hackathon, we must protect our IP.
* **`main` branch (Public):** Contains Universal Core + `public_adapters/`. Pushed to GitHub.
* **`hackathon` branch (Corporate):** Contains Universal Core + `public_adapters/` + `internal_adapters/`. Pushed ONLY to the internal corporate Git server.

By physically separating the adapters into `public_adapters/` and `internal_adapters/`, and using YAML to dynamically load them, the Universal Core never has to explicitly import or "know" about the secure corporate code.