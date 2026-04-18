import importlib
import logging
import json
import asyncio
import collections
import pathlib
import sys
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

try:
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry import trace
    import opentelemetry.sdk.trace as trace_sdk
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

class MemoryLogHandler(logging.Handler):
    def __init__(self, capacity=100):
        super().__init__()
        self.buffer = collections.deque(maxlen=capacity)
        self.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    def emit(self, record):
        self.buffer.append({
            "level": record.levelname,
            "message": self.format(record),
            "time": record.created
        })


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import jinja2
except ImportError:
    jinja2 = None

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
    from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse, JSONResponse
except ImportError:
    FastAPI = None

# Assuming google_adk provides LlmAgent. Adjust import if needed based on actual adk module.
try:
    from google_adk import LlmAgent
except ImportError:
    # Fallback for LlmAgent using litellm directly
    try:
        from litellm import acompletion
        import litellm
    except ImportError:
        acompletion = None
        litellm = None

    class LlmAgent:
        def __init__(self, **kwargs):
            # Map standard model names to litellm prefixes if necessary. 
            # Default to gemini/gemini-2.5-flash
            model = kwargs.get("model", "gemini-2.5-flash")
            if "gemini" in model and not model.startswith("gemini/"):
                model = f"gemini/{model}"
            self.model = model
            self.temperature = kwargs.get("temperature", 0.7)

        async def generate_content(self, prompt: str) -> str:
            if not acompletion:
                logger.warning("litellm is not installed. Returning empty JSON stub.")
                return "{}"
            
            max_retries = 3
            base_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = await acompletion(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature
                    )
                    return response.choices[0].message.content
                except litellm.ServiceUnavailableError as e:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"LLM Service Unavailable. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"LLM Generation Error: Service Unavailable after {max_retries} attempts.")
                        raise e
                except Exception as e:
                    logger.error(f"LLM Generation Error: {str(e)}")
                    raise e
                
        async def ping(self):
            """Fast-fail probe test."""
            if not acompletion:
                return True
            await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )

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

    def __init__(self, config: Dict[str, Any], mock_infrastructure: bool = False, enable_studio: bool = False):
        """
        Initialize the Chassis. 
        `config` should be the merged configuration (e.g., fleet.yaml + config.yaml).
        `mock_infrastructure` forces the chassis to use lightweight, in-memory adapters, bypassing the config.
        """
        self.config = config
        self.infrastructure_config = self.config.get("infrastructure", {})
        
        # 1. Instantiate the ADK LlmAgent
        agent_config = self.config.get("agent", {})
        self.llm_agent = LlmAgent(**agent_config)
        
        # Check environment variable override
        import os
        if os.getenv("MOCK_INFRASTRUCTURE", "").lower() in ("true", "1", "yes"):
            mock_infrastructure = True

        # 2. Load infrastructure adapters
        if mock_infrastructure:
            logger.info("Initializing Chassis with MOCK infrastructure.")
            from .mock_adapters import (
                MockStateStore, MockMessageQueue, MockVectorStore, 
                MockFileStorage, MockTelemetry, MockMCPServer
            )
            self.state_store = MockStateStore(self.config)
            self.message_broker = MockMessageQueue(self.config)
            self.vector_store = MockVectorStore(self.config)
            self.file_storage = MockFileStorage(self.config)
            self.telemetry = MockTelemetry(self.config)
            self.mcp_server = MockMCPServer(self.config)
        else:
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
        self.enable_studio = enable_studio
        self.studio_log_handler = None
        self.studio_span_exporter = None
        
        if self.enable_studio:
            self.studio_log_handler = MemoryLogHandler(capacity=100)
            self.studio_log_handler.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(self.studio_log_handler)
            
            if OTEL_AVAILABLE:
                self.studio_span_exporter = InMemorySpanExporter()
                provider = trace.get_tracer_provider()
                if isinstance(provider, trace_sdk.TracerProvider):
                    provider.add_span_processor(SimpleSpanProcessor(self.studio_span_exporter))

        self.app = FastAPI(title="BaseAgentChassis API")
        self.app.state.chassis = self
        self._register_routes()
        self._background_tasks = []

    async def start(self):
        """
        Start the chassis lifecycle:
        1. Launch all consumers registered via @consume_task as background tasks.
        """
        if hasattr(self, '_consumers'):
            for consumer in self._consumers:
                task = asyncio.create_task(consumer())
                self._background_tasks.append(task)
            logger.info(f"Launched {len(self._consumers)} background consumers.")

    def run_local(self, host: str = "0.0.0.0", port: int = 8000, quiet: bool = False):
        """
        Boot the Uvicorn/FastAPI server to serve the chassis locally.
        This is a blocking call and should be the entry point for running the application.
        """
        try:
            import uvicorn
        except ImportError:
            raise RuntimeError("uvicorn is required to run the local server. Install with `pip install uvicorn`")
        
        import os
        import sys
        import argparse
        
        parser = argparse.ArgumentParser(description="Run BaseAgentChassis")
        parser.add_argument("--quiet", "-q", action="store_true", help="Reduce console log output")
        args, _ = parser.parse_known_args()
        if args.quiet:
            quiet = True

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        console_handler = next((h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)), None)
        if not console_handler:
            console_handler = logging.StreamHandler(sys.stdout)
            root_logger.addHandler(console_handler)
        
        if quiet:
            console_handler.setLevel(logging.INFO)
        else:
            console_handler.setLevel(logging.DEBUG)

        # Startup Logging for LLM Probe
        model_str = getattr(self.llm_agent, 'model', 'Unknown')
        api_key = os.getenv("GEMINI_API_KEY", "")
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "Not Set or Too Short"
        
        logger.info(f"--- Booting Local Chassis ---")
        logger.info(f"Target LLM Model: {model_str}")
        logger.info(f"Using API Key: {masked_key}")
        
        # Attach the start method and probe to FastAPI startup event
        @self.app.on_event("startup")
        async def startup_event():
            logger.info("Executing LLM Probe Test...")
            try:
                if hasattr(self.llm_agent, 'ping'):
                    await self.llm_agent.ping()
                logger.info("✅ LLM Probe Successful! API connection is solid.")
            except Exception as e:
                logger.critical(f"❌ CRITICAL LLM PROBE FAILURE: {str(e)}")
                logger.critical("Check your API key and model string. Shutting down application.")
                # We use os._exit here because raising SystemExit inside an asyncio event loop 
                # might just be caught by the server rather than hard killing the process.
                os._exit(1)
            
            await self.start()
            
        logger.info(f"Starting BaseAgentChassis on http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

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

        @self.app.get("/")
        async def root_redirect():
            return RedirectResponse(url="/studio")

        @self.app.get("/studio/api/config")
        async def get_studio_config(request: Request):
            chassis = request.app.state.chassis
            if not chassis.enable_studio:
                return JSONResponse({})
            
            return JSONResponse({
                "model": getattr(chassis.llm_agent, "model", "Unknown"),
                "system_prompt": chassis.config.get("agent", {}).get("system_prompt", ""),
                "tools": chassis.config.get("agent", {}).get("tools", []),
                "skills": chassis.config.get("agent", {}).get("skills", [])
            })

        @self.app.get("/studio/api/telemetry")
        async def get_studio_telemetry(request: Request):
            chassis = request.app.state.chassis
            if not chassis.enable_studio or not chassis.studio_span_exporter:
                return JSONResponse([])
                
            spans = chassis.studio_span_exporter.get_finished_spans()
            spans = spans[-500:]
            
            serialized = []
            for span in spans:
                attributes = {}
                if span.attributes:
                    for k, v in span.attributes.items():
                        try:
                            attributes[k] = json.loads(v) if isinstance(v, str) and (v.startswith('{') or v.startswith('[')) else v
                        except:
                            attributes[k] = v
                            
                span_type = "unknown"
                name_lower = span.name.lower()
                if "user" in name_lower: span_type = "user"
                elif "llm" in name_lower or "generate" in name_lower: span_type = "llm"
                elif "tool" in name_lower: span_type = "tool"
                
                if not span.status.is_ok:
                    span_type = "error"
                    
                duration_ms = (span.end_time - span.start_time) / 1000000 if span.end_time and span.start_time else 0
                
                serialized.append({
                    "span_id": format(span.context.span_id, '016x'),
                    "trace_id": format(span.context.trace_id, '032x'),
                    "name": span.name,
                    "type": span_type,
                    "duration_ms": round(duration_ms, 2),
                    "attributes": attributes
                })
                
            return JSONResponse(serialized)

        @self.app.get("/studio/api/logs")
        async def get_studio_logs(request: Request):
            chassis = request.app.state.chassis
            if not chassis.enable_studio or not chassis.studio_log_handler:
                return HTMLResponse("<div class='text-gray-500'>Logs disabled.</div>")
                
            import html as html_lib
            html_fragments = []
            for record in chassis.studio_log_handler.buffer:
                level = record["level"]
                msg = record["message"]
                
                color = "text-gray-400"
                if level == "INFO": color = "text-blue-400"
                elif level == "WARNING": color = "text-yellow-400"
                elif level in ("ERROR", "CRITICAL"): color = "text-red-500 font-bold"
                
                msg_escaped = html_lib.escape(msg)
                html_fragments.append(f"<div class='{color} mb-1'>{msg_escaped}</div>")
                
            if not html_fragments:
                return HTMLResponse("<div class='text-gray-500 italic'>Waiting for first request...</div>")
            return HTMLResponse("".join(html_fragments))

        @self.app.get("/studio", response_class=HTMLResponse)
        async def get_studio(request: Request):
            """Returns the Agent Studio UI."""
            chassis = request.app.state.chassis
            if not chassis.enable_studio:
                raise HTTPException(status_code=404, detail="Studio disabled.")
                
            agent_name = self.config.get("agent", {}).get("name", "Agent")
            model_name = getattr(self.llm_agent, "model", "Unknown")
            
            template_path = pathlib.Path(__file__).parent / "studio.html"
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
            except FileNotFoundError:
                raise HTTPException(status_code=500, detail="Studio template not found.")
            
            html_content = html_content.replace("{{ agent_name }}", str(agent_name))
            html_content = html_content.replace("{{ agent_name_short }}", str(agent_name)[:3].upper())
            html_content = html_content.replace("{{ model_name }}", str(model_name))
            
            return html_content

        from fastapi import Form
        @self.app.post("/chat")
        async def chat_handler(
            message: str = Form(""),
            user_id: str = Form("studio_user"),
            session_id: str = Form("studio_session"),
            tenant_id: str = Form("local_dev"),
            file: Optional[UploadFile] = File(None)
        ):
            """Backend sync handler for the Agent Studio UI."""
            file_id = None
            if file and self.file_storage:
                content = await file.read()
                file_id = await self.file_storage.save_file(file.filename, content)
            
            # Since this is a generic chassis, we don't know the exact payload_model
            # of the target agent. For the mock studio, we will attempt to find 
            # a registered consumer and route to it dynamically, or return a generic mock response.
            
            if not hasattr(self, '_consumers') or not self._consumers:
                # No agents registered, return a default mock response
                return {"response": f"I received your message: '{message}'. No agents are currently registered to process it."}
            
            try:
                # Get the first registered consumer as the target for the Studio UI
                consumer = self._consumers[0]
                target_func = consumer.func
                payload_model = consumer.payload_model
                
                context = AgentContext(user_id=user_id, session_id=session_id, tenant_id=tenant_id)
                
                # Dynamically translate the raw chat message into the required structured payload
                prompt = f"Extract the user's intent from the following chat message into the required JSON payload schema. If any required fields are missing from the user's message, infer them or provide reasonable placeholder defaults (e.g., 'Unknown', 'N/A', or a generic name)."
                prompt += f"\nUser Message: {message}"
                if file_id:
                    prompt += f"\n[Attached File ID: {file_id}]"
                    
                structured_payload = await self.ask_structured(prompt, payload_model)
                
                # Execute the target agent function directly
                agent_response = await target_func(structured_payload, context)
                
                # Format the response back to the UI
                if hasattr(agent_response, 'model_dump_json'):
                    response_json = agent_response.model_dump_json(indent=2)
                else:
                    response_json = json.dumps(agent_response) if isinstance(agent_response, dict) else str(agent_response)
                    
                # Synthesize a conversational reply from the JSON payload
                synthesis_prompt = f"You are a helpful AI Agent. Synthesize this structured agent payload into a direct, friendly reply for the user. IMPORTANT: Provide ONLY the final synthesized message. Do NOT include any conversational filler, meta-commentary, or introductory phrases like 'Here is a friendly reply' or 'Of course!'. Do not include markdown code blocks unless explaining code.\n\nPayload:\n{response_json}"
                conversational_reply = await self.llm_agent.generate_content(synthesis_prompt)
                
                return {"response": conversational_reply}
                
            except Exception as e:
                logger.error(f"Studio chat error: {e}")
                return {"response": f"Error processing message: {str(e)}"}

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

    def consume_task(self, queue_name: str, payload_model: Type[T], max_retries: int = 3):
        """
        Decorator to continuously poll the message broker, deserialize payloads, and route to the wrapped function.
        """
        def decorator(func):
            async def wrapper():
                if not self.message_broker:
                    logger.error(f"Cannot consume queue '{queue_name}' without a configured message_broker.")
                    return
                
                logger.info(f"Starting consumer loop for queue: {queue_name}")
                while True:
                    try:
                        # 1. Listen for raw message
                        raw_message = await self.message_broker.listen(queue_name)
                        if not raw_message:
                            continue
                            
                        # Assuming the broker returns a dict with 'payload' and 'context'
                        # In a real implementation, the BaseMessageBroker ABC should define this return type.
                        payload_data = raw_message.get("payload", {})
                        context_data = raw_message.get("context", {})
                        
                        # 2. Deserialize
                        payload = payload_model(**payload_data)
                        context = AgentContext(**context_data)
                        
                        logger.info(f"Processing task on {queue_name} for session {context.session_id}")
                        
                        # 3. Route to wrapped function
                        await func(payload, context)
                        
                        # Note: DLQ routing and webhook response logic would go here, 
                        # catching exceptions from func() and tracking retries.
                        
                    except ValidationError as ve:
                        logger.error(f"Failed to deserialize payload for queue {queue_name}: {str(ve)}")
                    except asyncio.CancelledError:
                        logger.info(f"Consumer loop for {queue_name} cancelled.")
                        break
                    except Exception as e:
                        logger.error(f"Error processing message from queue {queue_name}: {str(e)}")
                        # Route to DLQ if max_retries exceeded...
            
            # We attach the wrapper to the chassis so it can be managed by the application lifecycle
            if not hasattr(self, '_consumers'):
                self._consumers = []
            
            # Attach metadata to the wrapper for dynamic routing in the Studio UI
            wrapper.payload_model = payload_model
            wrapper.func = func
            wrapper.queue_name = queue_name
            
            self._consumers.append(wrapper)
            return wrapper
        return decorator