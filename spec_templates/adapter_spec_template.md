# 🔌 Infrastructure Adapter Specification Template

**Adapter Name:** [e.g., CorpKafkaQueueAdapter]
**Target Interface (Port):** [e.g., `BaseMessageQueue` from `src/universal_core/interfaces.py`]
**Environment:** [e.g., Corporate K3s Cluster / Internal Hackathon]
**Location:** [e.g., `src/infrastructure/internal_adapters/`]

## 1. Purpose & Scope
[Briefly describe what this adapter connects to and why it's needed. E.g., "Connects the chassis to the internal corporate Kafka event bus for secure message passing."]

## 2. Dependencies
- **Python Packages:** [e.g., `confluent-kafka==2.3.0`]
- **External Systems:** [e.g., Corporate Kafka Cluster at `kafka.internal.corp:9092`]
- **Authentication/Secrets:** [e.g., mTLS certificates mounted via Vault, or specific env vars]

## 3. Configuration Schema (Pydantic)
[Define the exact Pydantic model required to configure this adapter via `config.yaml` or environment variables. This ensures validation at startup.]
```python
class AdapterConfig(BaseModel):
    # Define fields here, e.g., broker_url: str
    pass
```

## 4. Implementation Requirements
- **Method Mapping:** [List the abstract methods from the interface and how they map to the external system's SDK. e.g., `publish()` maps to `producer.produce()`]
- **Error Handling:** [Specify how exceptions from the external system should be caught and wrapped in standard Chassis exceptions so the Core doesn't crash unexpectedly]
- **Lifecycle:** [Describe initialization `__init__`, startup connections, and graceful shutdown/cleanup procedures]

## 5. Security & Guardrails
- [e.g., "Do not log payload contents, only metadata"]
- [e.g., "Must respect the corporate proxy settings"]
- [e.g., "Must assume zero-trust network"]

## 6. Testing Strategy
- **Unit Tests:** [How to mock the external system]
- **Integration Tests:** [How to test against a live/dev instance if available]