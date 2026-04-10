---
tags:
  - template/agent
  - architecture
status: Draft
---
# Agent Spec: {{title}}

*Note: The `BaseAgentChassis` handles all infrastructure. You only need to define the business logic here. Leave optional fields blank to use safe fleet defaults.*

## 1. Identity & Config
*   **Name:** {{title}}
*   **Model:** (Optional - Defaults to fleet `config.models.default`)
*   **Skills to Load:** (Optional - e.g., `web_scraper`, `sql_analyst`)

## 2. Triggers & Routing
*   **Queue Name:** (Optional - Defaults to `{{title}}_jobs`)
*   **Priority:** (Optional - Defaults to standard async execution)

## 3. The Contracts (Pydantic Models)
*   **Incoming Payload:** (Required - Describe the data this agent receives)
*   **State Model (JSONB):** (Optional - Defaults to a simple `AgentState` with `status: str`)
*   **Final Output:** (Required - Describe the final JSON response)

## 4. Prompts (`prompts/`)
*   **Core Directive:** (Required - What is the agent's main objective and persona?)
*   **Template Variables:** (Optional - List dynamic variables to inject. `user_id`, `session_id`, `tenant_id` are auto-injected by the Chassis).

## 5. Custom Tools (`tools.py`)
*   (Optional - List any custom Python functions this agent needs to execute).

## 6. Testing & Evaluation
*   (Optional - Defaults to `pytest` with mocked `execute_task` and `mock_infrastructure=True`).
