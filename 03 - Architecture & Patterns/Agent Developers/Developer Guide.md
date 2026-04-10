---
links:
  - "[Conceptual Guide - What is an Agent](Conceptual%20Guide%20-%20What%20is%20an%20Agent.md)"
  - "[Agent Directing Guide](Agent%20Directing%20Guide.md)"
---
# AI Agent Developer Guide: Building with the BaseAgentChassis

**Tags:** #developer-guide #python #adk #chassis
**Status:** Active Reference

Welcome to the fleet. This guide demonstrates the Developer Experience (DX) for creating a new agent in our distributed architecture. 

> **💡 Architecture Methodology:** 
> The architecture and design patterns outlined in this guide were developed using a rigorous, iterative process. If you need to design new systems, extend this architecture, or understand the meta-process we used to arrive at these decisions, refer to the `[Architecture Planning Skill](Architecture%20Planning%20Skill.md)` document.

Because the `BaseAgentChassis` handles all the distributed plumbing (FastAPI, Redis, PostgreSQL, OpenTelemetry, and K3s Health Checks), your job as an Agent Developer is strictly focused on **Business Logic**: Prompts, Tools, and State.

---

## Quick Start & Core Concepts
**The Golden Rule:** The `BaseAgentChassis` handles all distributed plumbing (Networking, Lifecycles, Observability). You *only* write Business Logic.

**The 5-Step Developer Workflow:**
1. **Configure (`config.yaml`):** Define your agent's name, model aliases, and which skills/tools to load.
2. **Define Schemas (`models.py`):** Create strict Pydantic models for your REST payloads and JSONB State.
3. **Write Prompts (`prompts/`):** Externalize all instructions into Jinja/Markdown templates.
4. **Write Tools (`tools.py`):** Write standard Python functions (the Chassis auto-registers them).
5. **Wire the Brain (`agent.py`):** Use the Chassis decorators to consume queues, update state, and trigger the LLM.

---

## 1. Standard Agent Directory Structure
When you create a new agent (e.g., the `ResearchAgent`), your repository or folder should look exactly like this:

```text
research_agent/
├── prompts/
│   └── system_prompt.jinja     # Externalized prompts
├── models.py                   # Pydantic schemas for State and API payloads
├── tools.py                    # Pure Python functions (ADK tools)
├── agent.py                    # The core logic and Chassis wiring
└── config.yaml                 # Agent-specific configuration (Name, Skills, Tools)
```

---

## 2. Agent Configuration (`config.yaml`)

This file is specific to the agent you are building. It defines the agent's identity and capabilities. 

> **Curious about defaults?** Database URIs, Redis endpoints, models, and telemetry settings are handled automatically by a global `fleet.yaml` file that is merged at runtime. If you want to understand how this deep merging works, see the `[BaseAgentChassis Internals](BaseAgentChassis%20Internals.md)` guide.

```yaml
# config.yaml
agent:
  name: "research_agent"  # The chassis will use this to identify itself on the network

# The chassis will automatically load these skills on startup
skills:
  - "web_scraper"
  - "data_analyst"

# The chassis will automatically import and register these functions from your tools.py file
tools:
  - "fetch_wikipedia_summary"
  - "calculate_confidence_score"
```

---

## 3. Defining Schemas & State (`models.py`)
Everything that goes over the network or into the database must be a strict Pydantic model. This ensures our AI coding tools don't hallucinate breaking API changes.

```python
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. The payload we expect to receive from the Router Agent
class ResearchTaskPayload(BaseModel):
    topic: str = Field(..., description="The core topic to research")
    max_sources: int = Field(default=5)
    requires_speed: bool = Field(default=False)

# 2. The internal state we save to PostgreSQL (JSONB)
class ResearchAgentState(BaseModel):
    current_status: str = "initializing"
    sources_analyzed: int = 0
    findings: List[str] = []
    
# 3. The structured output we want the LLM to generate
class ResearchSummary(BaseModel):
    executive_summary: str
    key_bullet_points: List[str]
    confidence_score: float
```

---

## 4. Externalizing Prompts (`prompts/system_prompt.jinja`)
Never hardcode massive prompts in Python. Use Jinja templates. This protects them from AI CLI refactoring and allows hot-reloading.

```jinja
You are the Deep Research Agent.
Your current task is to research: {{ topic }}

Core Directives:
1. You must analyze up to {{ max_sources }} sources.
2. Only use verified data.
3. If you encounter a corrupted file, skip it and continue.

User Context:
You are performing this research for user: {{ user_id }}
```

---

## 5. Writing Tools (`tools.py`)
Write standard Python functions. Because they are listed in your `config.yaml`, the Chassis will automatically import them and wrap them in ADK OpenTelemetry tracing spans when the agent boots.

```python
import httpx

async def fetch_wikipedia_summary(topic: str) -> str:
    """Fetches the summary of a topic from Wikipedia."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json().get("extract", "No data found.")
        return "Error fetching data."
```

---

## 6. Wiring the Agent (`agent.py`)

In this guide, we are building a hypothetical **Basic Research Agent** to demonstrate the workflow. It's important to distinguish between the mandatory **structural boilerplate** required by the Chassis and the custom **business logic** specific to this research task.

Because the `BaseAgentChassis` handles all the distributed plumbing, your job as an Agent Developer is strictly focused on Business Logic. `agent.py` acts strictly as the Controller (or the "Brain"). It handles the dynamic business logic, orchestration, and state mutations that cannot be hardcoded in a YAML file.

```python
import asyncio
from chassis import BaseAgentChassis, AgentContext

from models import ResearchTaskPayload, ResearchAgentState, ResearchSummary

# ==========================================
# STRUCTURE: Initialize the Chassis FIRST
# ==========================================
# Automatically loads fleet.yaml and config.yaml, merging them.
# Automatically loads the ADK agent, default models, skills, and tools!
chassis = BaseAgentChassis()

# ==========================================
# STRUCTURE: The Async Worker Decorator
# ==========================================
@chassis.consume_task(queue_name="research_jobs", state_model=ResearchAgentState, max_retries=3)
async def process_research_job(payload: ResearchTaskPayload, context: AgentContext, state: ResearchAgentState):
    """
    This function automatically listens to Redis. If it crashes 3 times,
    the Chassis routes the payload to the Dead Letter Queue (DLQ).
    State is automatically loaded, injected via the 'state' parameter, and saved on exit!
    """
    
    # ------------------------------------------
    # BUSINESS LOGIC: Update State & Rules
    # ------------------------------------------
    state.current_status = "researching"
    
    # Dynamic model swapping based on the user's payload
    if payload.requires_speed:
        chassis.adk_agent.model = chassis.config.models.fast

    # ------------------------------------------
    # STRUCTURE: Execute task
    # ------------------------------------------
    # Prompt loading, LLM execution, and strict JSON validation in one call.
    # Note: user_id and session_id are automatically injected from `context` into the Jinja template!
    result = await chassis.execute_task(
        template="system_prompt.jinja",
        template_vars={"topic": payload.topic, "max_sources": payload.max_sources},
        response_model=ResearchSummary,
        context=context
    )
    
    # ------------------------------------------
    # BUSINESS LOGIC: Custom Metrics
    # ------------------------------------------
    chassis.record_metric("research_completed", 1, {"topic": payload.topic})
    
    # ------------------------------------------
    # STRUCTURE: Auto-Reply
    # ------------------------------------------
    # Just return the result. The decorator handles the webhook!
    return result

# ==========================================
# DEPLOYMENT & LOCAL TESTING
# ==========================================

# A. STRUCTURE: For Kubernetes/Docker Deployment (FastAPI wrapper)
app = chassis.get_app()

# B. STRUCTURE: For Local Dev Testing (Bypasses Redis/Postgres/OTel)
if __name__ == "__main__":
    test_context = AgentContext(user_id="dev_1", session_id="test_sess", trace_id="123")
    test_payload = ResearchTaskPayload(topic="Quantum Computing", max_sources=2, requires_speed=True)
    
    # Runs the logic in the terminal instantly
    asyncio.run(chassis.run_local(
        func=process_research_job,
        payload=test_payload,
        context=test_context,
        mock_infrastructure=True
    ))
```

## 7. Running & Deploying the Agent
Now that the agent is wired up, you have three ways to execute it depending on your current development phase.

### A. Local Terminal Testing (Fastest Iteration)
Because we built `mock_infrastructure=True` into the Chassis, you can test the core reasoning, tool usage, and prompt logic without spinning up Postgres, Redis, or OpenTelemetry. Just run the Python file directly:
```bash
# Ensure your virtual environment is active
python agent.py
```
*This executes the `if __name__ == "__main__":` block, running the agent locally and outputting the execution trace directly to your console.*

### B. Local Fleet Orchestration (Docker Compose)
When you need to test how the agent interacts with PostgreSQL, Redis, or other agents, you spin up the local fleet. The chassis automatically exposes the FastAPI app.
```bash
# Builds the container and starts the distributed fleet via Colima/Podman
docker compose up --build research_agent
```
*Note: Because our architecture is strictly OCI-compliant, the `docker compose` command will seamlessly route through Colima (Apple native virtualization) on macOS, or Podman on corporate environments, without changing the command or the YAML file. The agent is now running as a microservice. It is listening for synchronous REST calls on `http://localhost:8000` and asynchronously consuming tasks from the Redis `research_jobs` queue.*

### C. Production Deployment (K3s / Linux Cluster)
Because the `BaseAgentChassis` strictly adheres to OCI container standards and exposes standard `/health` and `/ready` endpoints, deploying to your K3s cluster requires zero code changes.
```bash
kubectl apply -f k8s/research-agent-deployment.yaml
```
*K3s will automatically handle load balancing, monitor the chassis health probes, and restart the pod if the agent enters an unrecoverable state.*