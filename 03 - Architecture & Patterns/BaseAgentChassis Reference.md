---
Status: Approved
status: Approved
---
# BaseAgentChassis Reference Skeleton

**Tags:** #architecture #python #chassis #adk
**Status:** Draft / Reference

This document outlines the Python skeleton for the `BaseAgentChassis`. It serves as the contract between our custom agent logic and our distributed infrastructure (Docker/K3s). 

By inheriting from this class, an agent developer (or an AI CLI) gets OpenTelemetry, health checks, Redis task queue publishing, PostgreSQL connection pooling, and Jinja prompt loading entirely for free.

## The Python Skeleton (`chassis.py`)

```python
import os
import yaml
import functools
import importlib
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Type, List, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from jinja2 import Environment, FileSystemLoader

# Google ADK Imports
from google_adk.server import get_fast_api_app
from google_adk.agent import BaseAgent, LlmAgent # Assuming the base classes from ADK

# Note: In the real implementation, these would be our actual DB/Redis adapters
# import asyncpg
# import redis.asyncio as redis
# import httpx
# from opentelemetry import trace, metrics

class AgentContext(BaseModel):
    """
    Standard wrapper passed alongside all inter-agent requests to guarantee 
    security, identity, and trace propagation across the distributed fleet.
    """
    user_id: str
    session_id: str
    tenant_id: Optional[str] = None
    trace_id: str
    reply_to: Optional[str] = None # Used for Auto-Reply Webhooks


class BaseAgentChassis:
    """
    The foundational microservice chassis for all deployed agents.
    Handles configuration, telemetry, DB/Redis lifecycles, and FastAPI wrapping.
    """

    def __init__(
        self, 
        config_path: str = "/app/config.yaml",
        prompts_dir: str = "/app/prompts",
        skills_dir: str = "/app/skills"
    ):
        self.config = self._load_config(config_path)
        
        # Externalized Agent Name from config.yaml
        self.agent_name = self.config.get("agent", {}).get("name", "unnamed_agent")
        
        # Setup Jinja Environment for hot-reloadable external prompts
        self.jinja_env = Environment(loader=FileSystemLoader(prompts_dir))
        self.skills_dir = skills_dir
        
        self.adk_agent = None
        
        # Placeholders for infrastructure clients
        self.db_pool = None
        self.redis_client = None
        self.http_client = None
        
        # Initialize OpenTelemetry (points to Arize Phoenix based on config)
        self.tracer, self.meter = self._setup_telemetry()
        
        # Automatically build the ADK Agent so the developer doesn't have to
        self.build_adk_agent()

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads the centralized configuration mounted via Docker/K3s."""
        if not os.path.exists(path):
            return {} # Fallback or raise error in prod
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_telemetry(self):
        """Bootstraps OpenTelemetry to emit traces and metrics to Arize Phoenix."""
        return None, None

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manages the cold start and graceful shutdown of the microservice."""
        # 1. Initialize PostgreSQL (pgvector) connection pool
        # 2. Initialize Redis connection for Async Queues
        # 3. Initialize reusable HTTP client for inter-agent communication
        yield # Application is running and accepting traffic
        # Gracefully close connections on shutdown

    # ==========================================
    # ABSTRACTION: ADK Initialization & Models
    # ==========================================
    def build_adk_agent(self, model_alias: str = "default"):
        """
        Initializes the ADK agent using model strings defined in the external config.yaml.
        Prevents hardcoding model versions in Python code.
        Automatically equips any skills and tools defined in the configuration.
        """
        # Retrieve the actual model string (e.g., "gemini-1.5-pro") from config.
        models_config = self.config.get("models", {})
        actual_model = models_config.get(model_alias, "gemini-1.5-pro")
        
        self.adk_agent = LlmAgent(
            model=actual_model,
            tools=[]
        )
        
        # Automatically equip skills defined in config.yaml
        for skill in self.config.get("skills", []):
            self.equip_skill(skill)
            
        # Automatically load and register tools defined in config.yaml from tools.py
        try:
            tools_module = importlib.import_module("tools")
            for tool_name in self.config.get("tools", []):
                if hasattr(tools_module, tool_name):
                    tool_func = getattr(tools_module, tool_name)
                    self.register_tool(tool_func)
                else:
                    print(f"Warning: Tool '{tool_name}' defined in config.yaml but not found in tools.py")
        except ImportError:
            print("Warning: tools.py module not found.")

    # ==========================================
    # ABSTRACTION: Prompt & Skill Management
    # ==========================================
    def load_prompt(self, template_name: str, **kwargs) -> str:
        """Loads a Jinja/Markdown prompt from disk and renders it with variables."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**kwargs)

    def equip_skill(self, skill_name: str):
        """
        Dynamically loads a skill bundle (Jinja instructions + Python tools).
        Appends the instructions to the agent's system prompt and registers its tools.
        """
        # 1. Read instructions from self.skills_dir / skill_name / instructions.jinja
        # 2. Append to self.adk_agent's system prompt
        # 3. Import tools.py from the skill bundle and call self.register_tool()
        pass

    # ==========================================
    # ABSTRACTION: Tool & MCP Registration
    # ==========================================
    def register_tool(self, tool_func: Callable):
        """
        Registers a standard Python tool with the ADK agent, automatically
        wrapping it in OpenTelemetry tracing spans.
        """
        # wrapped_tool = apply_otel_tracing(tool_func)
        # self.adk_agent.tools.append(wrapped_tool)
        pass

    async def connect_mcp_sandbox(self, server_url: str):
        """
        Connects to an external, heavily isolated Model Context Protocol (MCP) server.
        Used strictly for safe code execution (sandboxing) so agents never run generated 
        code natively within their own container.
        """
        pass

    # ==========================================
    # ABSTRACTION: Asynchronous Communication
    # ==========================================
    async def publish_async_task(self, queue_name: str, payload: BaseModel, context: AgentContext):
        """
        Drops a long-running task for another agent into the Redis queue.
        Automatically injects the AgentContext for secure routing.
        """
        pass

    def consume_task(self, queue_name: str, state_model: Optional[Type[BaseModel]] = None, max_retries: int = 3):
        """
        Decorator: Registers a method to continuously listen to a Redis queue.
        Abstracts away the `while True: BLPOP` loop and extracts the AgentContext.
        
        State Injection: If a `state_model` is provided, the decorator automatically 
        loads the state from Postgres (or initializes a new one), injects it as a kwarg 
        into the decorated function, and automatically saves it back when the function exits.
        
        DLQ Implementation: If the task fails `max_retries` times (poison pill),
        it automatically routes the payload to `{queue_name}_dlq` and emits an alert.
        
        Auto-Reply Implementation: If the decorated function returns a Pydantic model,
        and `context.reply_to` is set, the decorator automatically makes a sync call
        back to the origin agent with the result.
        """
        def decorator(func):
            # Register the background task to start during lifespan
            return func
        return decorator

    # ==========================================
    # ABSTRACTION: Synchronous Communication & Resiliency
    # ==========================================
    def with_retry(max_attempts: int = 3, backoff: bool = True):
        """
        Decorator: Adds exponential backoff and retry logic to network calls.
        Crucial for protecting against transient inter-agent API failures.
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Retry logic implementation here
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    @with_retry(max_attempts=3)
    async def call_agent_sync(self, target_agent: str, endpoint: str, payload: BaseModel, context: AgentContext) -> Dict[str, Any]:
        """
        Makes a synchronous REST call to another agent in the cluster.
        Automatically injects the AgentContext header. Handles internal DNS 
        (K3s/Docker), timeouts, retries, and OTel trace IDs.
        """
        pass

    # ==========================================
    # ABSTRACTION: Strict Structured Outputs & Execution
    # ==========================================
    async def ask_structured(self, prompt: str, response_model: Type[BaseModel], max_retries: int = 3) -> BaseModel:
        """
        Forces the LLM to return strict JSON matching a Pydantic schema.
        If it fails validation, it automatically feeds the ValidationError back
        to the LLM with a hidden turn to self-correct.
        """
        # formatted_prompt = inject_schema(prompt, response_model)
        # for attempt in range(max_retries):
        #     response = await self.adk_agent.arun(formatted_prompt)
        #     try:
        #         return response_model.model_validate_json(response)
        #     except ValidationError as e:
        #         formatted_prompt = f"Validation Error: {e}. Please fix the JSON."
        # raise ValueError("Max retries exceeded for structured output.")
        pass

    async def execute_task(self, template: str, template_vars: Dict[str, Any], response_model: Type[BaseModel], context: AgentContext) -> BaseModel:
        """
        Mega-Abstraction: Auto-injects security context variables (user_id, session_id), 
        loads the Jinja prompt, sets the ADK system prompt, and calls ask_structured 
        in a single line of code.
        """
        # Auto-inject context variables so the developer doesn't have to
        # template_vars.update({
        #     "user_id": context.user_id,
        #     "session_id": context.session_id,
        #     "tenant_id": context.tenant_id
        # })
        # self.adk_agent.system_prompt = self.load_prompt(template, **template_vars)
        # return await self.ask_structured("Execute task", response_model)
        pass

    # ==========================================
    # ABSTRACTION: Semantic Memory & State
    # ==========================================
    async def semantic_search(self, query: str, context: AgentContext, limit: int = 5) -> List[Dict[str, Any]]:
        """Embeds a query and searches pgvector, scoped strictly by the AgentContext."""
        pass

    async def save_state(self, key: str, value: BaseModel, context: AgentContext):
        """Upserts structured session state as JSONB into Postgres, scoped by AgentContext."""
        pass

    async def load_state(self, key: str, target_model: Type[BaseModel], context: AgentContext) -> Optional[BaseModel]:
        """Retrieves structured state from Postgres, scoped by AgentContext."""
        pass

    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Emits a custom business metric to the telemetry backend."""
        pass

    # ==========================================
    # SERVER DEPLOYMENT & LOCAL EXECUTION
    # ==========================================
    def get_app(self) -> FastAPI:
        """Wraps the ADK Agent in FastAPI with strict K3s health probes."""
        app = get_fast_api_app(self.adk_agent, lifespan=self.lifespan)
        # ... health check endpoints ...
        return app

    async def run_local(self, prompt: str, mock_infrastructure: bool = True):
        """
        Allows local REPL/terminal testing by gracefully bypassing
        Postgres/Redis/OTel if mock_infrastructure=True.
        """
        pass
```