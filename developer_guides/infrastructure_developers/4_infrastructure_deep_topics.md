# 4. Deep Topics (Advanced Reading)

**Status:** Post-Hackathon / Homework
**Target Audience:** Infrastructure Developers and Platform Engineers.

This guide goes deep into the weeds of enterprise-grade deployments, observability, and distributed systems. It is not required for the initial hackathon setup but is crucial for production.

## 1. Advanced Telemetry & Distributed Tracing

When you have multiple agents talking to each other via Redis queues, tracking a single user request becomes complex.

### OpenTelemetry (Arize Phoenix) Injection
The `BaseAgentChassis` natively supports OpenTelemetry. To trace a request across boundaries:
*   Ensure the `trace_id` is included in the Redis message payload.
*   When the consumer picks up the task, it must start a new span using that `trace_id` as the parent.
*   This allows you to see the full lifecycle in your Phoenix dashboard: *User Request -> Agent A -> Redis -> Agent B -> DB Write*.

## 2. Dead Letter Queues (DLQ) & Resilience

What happens if an agent crashes while processing a task?
*   **Acknowledge (ACK) Strategy:** Do not ACK the Redis message until the task is completely finished and the state is saved to Postgres.
*   **DLQ Routing:** If a task fails 3 times, the adapter should automatically route it to a `dead_letter_queue` in Redis.
*   **Recovery:** Build a separate utility script that allows engineers to inspect the DLQ and replay messages once the bug is fixed.

## 3. Postgres JSONB Indexing Strategies (pgvector)

As your agent's state grows, querying it can become slow.
*   Do not index the entire JSONB state blob.
*   Create specific GIN indexes on the keys that the agent queries frequently (e.g., `CREATE INDEX idx_state_status ON agent_state USING GIN ((state->>'status'));`).
*   For semantic memory, ensure your `pgvector` tables are segregated by `agent_id` or `tenant_id` to prevent cross-contamination and speed up cosine similarity searches.