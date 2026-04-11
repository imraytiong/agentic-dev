---
tags:
  - template/infrastructure
  - platform
status: Active
---
# Fleet Infrastructure Spec (The Blueprint)

*Provide this document to the [adk-infra-builder](../08%20-%20AI%20CLI%20Skills/adk-infra-builder.md) skill to bootstrap the cluster's operational adapters.*

## 1. Core Runtime
*   **Python Version:** 3.11-slim
*   **Package Manager:** `pip` (keep it standard for the hackathon)
*   **Core Dependencies:** `google-adk`, `fastapi`, `uvicorn`, `pydantic>2.0`, `asyncpg`, `opentelemetry-sdk`, `jinja2`, `pyyaml`. *(Note: Message broker client will depend on the chosen adapter).*

## 2. Infrastructure Containers (docker-compose.yml)
*   **Strict OCI Compliance:** Must be 100% OCI-compliant. Do NOT use Docker Desktop proprietary features (like Docker Extensions or specific Docker Desktop bind mounts). This file must run flawlessly on `podman-compose` and `colima`.
*   **Database:** `pgvector/pgvector:pg16`
    *   Port: `5432:5432`
    *   Env: `POSTGRES_USER=agent`, `POSTGRES_PASSWORD=hackathon`, `POSTGRES_DB=agent_db`
*   **Message Broker:** *(To be determined by environment. e.g., Redis, RabbitMQ, or NATS).*
*   **Observability:** `arizeai/phoenix:latest`
    *   Ports: `6060:6060` (UI), `4317:4317` (OTel gRPC)

## 3. Global Configuration (fleet.yaml)
*   **Models:** `default: gemini-1.5-flash`, `reasoning: gemini-1.5-pro`
*   **Database URI:** `postgresql+asyncpg://agent:hackathon@postgres:5432/agent_db`
*   **Message Broker URI:** `amqp://...` or `redis://...` *(Depends on the chosen broker)*
*   **Telemetry Endpoint:** `http://arize-phoenix:4317`
*   **Infrastructure Plugin Mapping:**
    ```yaml
    infrastructure:
      state_store: "adapters.postgres.PostgresStateStore"
      vector_store: "adapters.postgres.PgVectorStore"
      message_broker: "adapters.redis.RedisBroker"
      telemetry: "adapters.telemetry.ArizePhoenixAdapter"
    ```

## 4. Operational Adapters to Build (`adapters/`)
The `BaseAgentChassis` Universal Core (`core/chassis.py`) is sealed. The AI CLI must implement the following adapters in the `adapters/` directory to replace the mock infrastructure:

1.  **State Store & Vector Store Adapters:** Implement classes inheriting from `BaseStateStore` and `BaseVectorStore`. Connect `save_state()` and `load_state()` to read/write to the state store using Pydantic models. Connect `semantic_search()` to execute semantic queries against the vector store.
2.  **Message Broker Adapter:** Implement a class inheriting from `BaseMessageBroker`. Connect `publish()` and `consume()` to interface with the chosen broker.
3.  **OpenTelemetry Adapter:** Configure the OTel SDK to export traces to the Arize Phoenix gRPC endpoint defined in `fleet.yaml`.