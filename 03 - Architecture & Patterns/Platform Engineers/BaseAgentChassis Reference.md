---
Status: Approved
status: Approved
---
# BaseAgentChassis Reference Skeleton

**Tags:** #architecture #python #chassis #adk
**Status:** Active Reference

This document outlines the Python skeleton for the `BaseAgentChassis`. It is divided into two parts: The **Universal Core** (which is pre-built and environment-agnostic) and the **Operational Adapters** (which the Infrastructure Team builds to connect to Docker/K3s).

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
from google_adk.agent import BaseAgent, LlmAgent

class AgentContext(BaseModel):
    user_id: str
    session_id: str
    tenant_id: Optional[str] = None
    trace_id: str
    reply_to: Optional[str] = None 

class BaseAgentChassis:
    def __init__(
        self, 
        config_path: str = "/app/config.yaml",
        fleet_config_path: str = "/app/fleet.yaml",
        prompts_dir: str = "/app/prompts",
        skills_dir: str = "/app/skills"
    ):
        # === UNIVERSAL CORE (PRE-BUILT) ===
        self.config = self._deep_merge_config(fleet_config_path, config_path)
        self.agent_name = self.config.get("agent", {}).get("name", "unnamed_agent")
        self.jinja_env = Environment(loader=FileSystemLoader(prompts_dir))
        self.skills_dir = skills_dir
        
        # === OPERATIONAL ADAPTERS (TO BE IMPLEMENTED) ===
        self.state_store_client = None
        self.vector_store_client = None
        self.message_broker_client = None
        self.tracer, self.meter = self._setup_telemetry()
        
        # === UNIVERSAL CORE (PRE-BUILT) ===
        self.build_adk_agent()

    # =========================================================================
    # UNIVERSAL CORE: Pre-built Logic (No external dependencies)
    # =========================================================================
    def _deep_merge_config(self, fleet_path: str, local_path: str) -> Dict:
        """Merges global fleet.yaml with local config.yaml."""
        pass

    def build_adk_agent(self, model_alias: str = "default"):
        """Automatically initializes the ADK agent, equips skills, and loads tools based on config."""
        pass

    def equip_skill(self, skill_name: str):
        """Loads Jinja instructions and appends to system prompt."""
        pass

    def register_tool(self, tool_func: Callable):
        """Registers a Python tool with ADK and wraps it in OTel."""
        pass

    async def execute_task(self, template: str, template_vars: Dict[str, Any], response_model: Type[BaseModel], context: AgentContext) -> BaseModel:
        """Mega-Abstraction: Auto-injects context variables, loads Jinja, and calls ask_structured."""
        pass

    async def ask_structured(self, prompt: str, response_model: Type[BaseModel], max_retries: int = 3) -> BaseModel:
        """Forces strict JSON output with auto-correction loops for ValidationErrors."""
        pass

    def consume_task(self, queue_name: str, state_model: Optional[Type[BaseModel]] = None, max_retries: int = 3):
        """
        Decorator: Handles background listening, state injection, and DLQ routing.
        If mock_infrastructure=True, uses asyncio.Queue. Otherwise uses Message Broker Adapter.
        """
        pass

    async def run_local(self, prompt: str, mock_infrastructure: bool = True):
        """Bypasses FastAPI and real DBs/Queues for instant terminal testing."""
        pass

    # =========================================================================
    # OPERATIONAL ADAPTERS: To be built by Infrastructure Team (Track A)
    # =========================================================================
    def _setup_telemetry(self):
        """ADAPTER: Configure OpenTelemetry to export to Arize Phoenix."""
        pass

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """ADAPTER: Initialize state/vector store clients and message broker client."""
        pass

    async def publish_async_task(self, queue_name: str, payload: BaseModel, context: AgentContext):
        """ADAPTER: Push serialized payload to the configured message broker."""
        pass

    @with_retry(max_attempts=3)
    async def call_agent_sync(self, target_agent: str, endpoint: str, payload: BaseModel, context: AgentContext) -> Dict[str, Any]:
        """ADAPTER: Make HTTP REST call to target agent using internal K3s/Docker DNS."""
        pass

    async def semantic_search(self, query: str, context: AgentContext, limit: int = 5) -> List[Dict[str, Any]]:
        """ADAPTER: Embed query and execute semantic search via vector_store_client. Returns standard Python lists."""
        pass

    async def save_state(self, key: str, value: BaseModel, context: AgentContext):
        """ADAPTER: Serialize and upsert Pydantic model into state_store_client."""
        pass

    async def load_state(self, key: str, target_model: Type[BaseModel], context: AgentContext) -> Optional[BaseModel]:
        """ADAPTER: Retrieve from state_store_client and validate into the target Pydantic model."""
        pass
```