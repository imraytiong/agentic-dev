---
tags:
  - template/agent
  - architecture
status: Draft
---
# Agent Name: {{title}}

## 1. Core Objective
*What is the primary goal of this agent? What problem does it solve?*

## 2. Persona & System Prompt
*How should this agent behave? What are its core instructions and constraints?*
*(Note: Keep Python code strictly for logic. Externalize prompt configuration where possible.)*

## 3. ADK Architecture & Patterns
*Which ADK primitives are used? (e.g., `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`)*

### 3.1 Tools & External Integrations
*List standard `FunctionTool` implementations and MCP integrations.*
- [ ] Tool 1 (Python function): *Description*
- [ ] Tool 2 (External API/MCP): *Description*

### 3.2 State & Memory Management
*How does this agent persist state across sessions? (e.g., PostgreSQL/SQLAlchemy for metadata, pgvector for semantic memory)*

### 3.3 Advanced RAG Approach
*Does this agent retrieve documents? If so, how is LlamaIndex (or custom retriever) wrapped inside an ADK tool?*

### 3.4 Lifecycle & Observability
*How is this agent initialized? What OpenTelemetry metrics are critical to trace? Are there specific `before_agent_prompt` or `after_agent_callback` hooks?*

## 4. Testing & Evaluation
*How do we assert correctness?*
- [ ] Unit tests written for tools (`pytest`)
- [ ] Agent eval criteria defined (e.g., DeepEval for faithfulness)

## 5. Development Log & Tasks
- [ ] Define initial prompt configuration
- [ ] Implement tools with Pydantic validation
- [ ] Wire up ADK Runner and FastAPI lifespan
- [ ] Test edge cases

---
## Notes & Iterations
*Log your testing results and prompt tweaks here.*