import importlib
import logging
import json
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

try:
    import jinja2
except ImportError:
    jinja2 = None

try:
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.responses import HTMLResponse, StreamingResponse
except ImportError:
    FastAPI = None

# Assuming google_adk provides LlmAgent. Adjust import if needed based on actual adk module.
try:
    from google_adk import LlmAgent
except ImportError:
    # Fallback/Mock for LlmAgent
    class LlmAgent:
        def __init__(self, **kwargs):
            pass
        async def generate_content(self, prompt: str) -> str:
            return "{}"

from .interfaces import (
    BaseStateStore,
    BaseVectorStore,
    BaseFileStorage,
    BaseMessageBroker,
    BaseTelemetry,
    BaseMCPServer,
    AgentContext
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def _deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge dict2 into dict1."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

class BaseAgentChassis:
    """
    The Universal Orchestration Engine.
    Dynamically loads environment-specific infrastructure via Inversion of Control.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Chassis. 
        `config` should be the merged configuration (e.g., fleet.yaml + config.yaml).
        """
        self.config = config
        self.infrastructure_config = self.config.get("infrastructure", {})
        
        # 1. Instantiate the ADK LlmAgent
        agent_config = self.config.get("agent", {})
        self.llm_agent = LlmAgent(**agent_config)

        # 2. Dynamically load infrastructure adapters
        self.state_store: Optional[BaseStateStore] = self._load_adapter(
            "state_store", BaseStateStore
        )
        self.vector_store: Optional[BaseVectorStore] = self._load_adapter(
            "vector_store", BaseVectorStore
        )
        self.file_storage: Optional[BaseFileStorage] = self._load_adapter(
            "file_storage", BaseFileStorage
        )
        self.message_broker: Optional[BaseMessageBroker] = self._load_adapter(
            "message_broker", BaseMessageBroker
        )
        self.telemetry: Optional[BaseTelemetry] = self._load_adapter(
            "telemetry", BaseTelemetry
        )
        self.mcp_server: Optional[BaseMCPServer] = self._load_adapter(
            "mcp_server", BaseMCPServer
        )

        logger.info("BaseAgentChassis initialized with dynamic infrastructure.")

        # 3. Initialize FastAPI App Embedded within the Chassis
        self.app = FastAPI(title="BaseAgentChassis API")
        self._register_routes()

    def _load_adapter(self, config_key: str, expected_type: type) -> Any:
        """
        Dynamically imports and instantiates an adapter class from a string path.
        Enforces that the loaded class implements the expected Interface (ABC).
        """
        plugin_path = self.infrastructure_config.get(config_key)
        if not plugin_path:
            logger.debug(f"No infrastructure configured for: {config_key}")
            return None

        try:
            module_path, class_name = plugin_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)
            
            if not issubclass(adapter_class, expected_type):
                raise TypeError(
                    f"Adapter '{plugin_path}' does not implement the expected "
                    f"interface '{expected_type.__name__}'."
                )
            
            # Instantiate and return the adapter with config
            return adapter_class(config=self.config)
        
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load adapter '{plugin_path}': {str(e)}")
            raise e

    def _register_routes(self):
        """Register all FastAPI routes for the chassis."""
        if not FastAPI:
            logger.warning("FastAPI not installed. Routes will not be available.")
            return

        @self.app.get("/studio", response_class=HTMLResponse)
        async def get_studio():
            """Returns the Agent Studio UI."""
            return """
            <html>
                <head>
                    <title>Agent Studio</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gray-100 h-screen flex flex-col items-center justify-center">
                    <h1 class="text-3xl font-bold mb-4">Agent Studio</h1>
                    <div class="bg-white p-6 rounded shadow-md w-1/2 h-1/2">
                        <p class="text-gray-500">Embedded chat interface goes here.</p>
                    </div>
                </body>
            </html>
            """

        @self.app.post("/upload")
        async def upload_file(file: UploadFile = File(...)):
            """Multimodal file upload."""
            if not self.file_storage:
                raise HTTPException(status_code=501, detail="File storage not configured.")
            
            content = await file.read()
            file_id = await self.file_storage.save_file(file.filename, content)
            return {"file_id": file_id, "filename": file.filename}

        @self.app.get("/download/{file_id}")
        async def download_file(file_id: str):
            """Outbound file route."""
            if not self.file_storage:
                raise HTTPException(status_code=501, detail="File storage not configured.")
            
            try:
                content = await self.file_storage.get_file(file_id)
                # In a real app we'd stream this or return FileResponse
                return {"file_id": file_id, "size": len(content)}
            except Exception as e:
                raise HTTPException(status_code=404, detail=str(e))

        @self.app.get("/mcp/sse")
        async def mcp_sse():
            """MCP Server route."""
            if not self.mcp_server:
                raise HTTPException(status_code=501, detail="MCP Server not configured.")
            
            stream = await self.mcp_server.start_sse_stream()
            return StreamingResponse(stream, media_type="text/event-stream")

    async def ask_structured(self, prompt: str, response_model: Type[T], max_retries: int = 3) -> T:
        """
        Executes a prompt against the LLM and enforces a structured Pydantic response.
        Includes a built-in retry loop for JSON healing.
        """
        schema = json.dumps(response_model.model_json_schema())
        augmented_prompt = f"{prompt}\n\nPlease respond in pure JSON matching this schema:\n{schema}"
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response_text = await self.llm_agent.generate_content(augmented_prompt)
                # Clean up potential markdown blocks
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()
                
                data = json.loads(cleaned_text)
                return response_model(**data)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Attempt {attempt + 1} failed. Healing JSON...")
                last_error = str(e)
                augmented_prompt += f"\n\nYour previous response failed validation: {last_error}. Please fix it."
        
        raise ValueError(f"Failed to generate structured response after {max_retries} attempts. Last error: {last_error}")

    async def execute_task(self, template_str: str, template_vars: dict, response_model: Type[T], context: AgentContext) -> T:
        """
        The core agentic loop.
        Loads Jinja template, injects AgentContext, renders prompt, and calls ask_structured.
        """
        if not jinja2:
            raise RuntimeError("jinja2 is required for execute_task.")
        
        env = jinja2.Environment()
        template = env.from_string(template_str)
        
        # Inject standard AgentContext variables
        template_vars['user_id'] = context.user_id
        template_vars['session_id'] = context.session_id
        template_vars['tenant_id'] = context.tenant_id
        
        rendered_prompt = template.render(**template_vars)
        return await self.ask_structured(rendered_prompt, response_model)
