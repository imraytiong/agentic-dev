---
links:
  - "[[conceptual_guide]]"
  - "[[agent_directing_guide]]"
---
# AI Agent Developer Guide: Building with the BaseAgentChassis

**Tags:** #developer-guide #python #adk #chassis
**Status:** Active Reference

Welcome to the fleet. This guide demonstrates the Developer Experience (DX) for creating a new agent in our distributed architecture. 

> **💡 Architecture Methodology:** 
> The architecture and design patterns outlined in this guide were developed using a rigorous, iterative process. If you need to design new systems, extend this architecture, or understand the meta-process we used to arrive at these decisions, refer to the `[[../../skills/architecture-planning/SKILL.md|Architecture Planning Skill]]` document.

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

> **Curious about defaults?** Database URIs, Redis endpoints, models, and telemetry settings are handled automatically by a global `fleet.yaml` file that is merged at runtime. If you want to understand how this deep merging works, see the `[[../infrastructure_developers/baseagentchassis_internals|BaseAgentChassis Internals]]` guide.

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
    
    # Runs the logic instantly using the Mock Engine and Agent Studio
    asyncio.run(chassis.run_local(
        func=process_research_job,
        payload=test_payload,
        context=test_context,
        mock_infrastructure=True
    ))
```

## 7. Testing & Interacting with your Agent

Once you've built your agent, you need to test it. Because we built the `BaseAgentChassis` with an "Open Core" philosophy, we provide two incredibly powerful ways to interact with your agent locally *without* needing a frontend developer. Both natively support **Multimodal inputs (File Uploads & Links)**!

### A. The "Agent Studio" (Local Web UI)
When you run `python agent.py` with `mock_infrastructure=True`, the Chassis automatically spins up the **Agent Studio**. 
This is an embedded, single-page web application served directly from FastAPI. 

1. Run `python agent.py`
2. Open your browser to `http://localhost:8000/studio`
3. **The Wow Factor:** You will instantly see a slick, dark-mode chat interface. 
4. **Files & Links:** Click the paperclip icon to upload PDFs, images, or code files, or just paste a URL. The FastAPI backend automatically parses the files and passes the content directly into the ADK state for the LLM to process!

### B. The IDE Integration (MCP Server)
The ultimate "cheat code" for testing is the **Model Context Protocol (MCP)**. Your `BaseAgentChassis` automatically exposes an MCP Server endpoint. This means your IDE can become the user interface!

1. Run `python agent.py` (either mocked or with full infrastructure).
2. Open an MCP-compatible IDE like **Cursor** or **Windsurf**.
3. Add a new MCP Server pointing to `http://localhost:8000/mcp/sse`.
4. **Files & Links:** You don't even need an upload button. Just highlight code in your IDE, use `@Files` to attach PDFs/documents, or paste a link. The IDE reads the file context and streams it securely to the running Python agent over MCP!

### C. Sending Files Back to the User (Outbound Multimodal)
Often, your agent will need to generate a report, a CSV, or modify an image and send it back to the user.
1. **The Tool:** You write a standard Python tool in `tools.py` that uses the Chassis's `BaseFileStorage` adapter (e.g., `chassis.file_storage.save_file(filename, data)`). This saves the file to local disk (Mac Mini) or an S3 bucket (Corporate K3s) and returns a `file_id`.
2. **The Response:** The agent simply responds with a Markdown link: `Here is your report: [Download Report](/download/12345)`.
3. **The Client:** 
   - **Agent Studio:** Automatically renders the Markdown link as a clickable download button that hits the Chassis's native `GET /download/{file_id}` FastAPI route.
   - **MCP (IDE):** The IDE parses the link, allowing the user to click it and download the file directly into their workspace.

### D. Fleet Orchestration (Docker Compose)
When you are done testing logic and need to test how the agent interacts with PostgreSQL, Redis, or other agents, you spin up the local fleet.
```bash
docker compose up --build research_agent
```
*Note: The agent is now running as a microservice, listening for synchronous REST calls on `http://localhost:8000` and asynchronously consuming tasks from the Redis queues.*

### E. Production Deployment (K3s / Linux Cluster)
Because the `BaseAgentChassis` strictly adheres to OCI container standards and exposes standard `/health` and `/ready` endpoints, deploying to your K3s cluster requires zero code changes.
```bash
kubectl apply -f k8s/research-agent-deployment.yaml
```