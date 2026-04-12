import importlib
import logging
import json
import asyncio
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

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
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.responses import HTMLResponse, StreamingResponse
except ImportError:
    FastAPI = None

# Assuming google_adk provides LlmAgent. Adjust import if needed based on actual adk module.
try:
    from google_adk import LlmAgent
except ImportError:
    # Fallback for LlmAgent using litellm directly
    try:
        from litellm import acompletion
    except ImportError:
        acompletion = None

    class LlmAgent:
        def __init__(self, **kwargs):
            # Map standard model names to litellm prefixes if necessary. 
            # Default to gemini-1.5-flash
            model = kwargs.get("model", "gemini/gemini-1.5-flash")
            if "gemini" in model and not model.startswith("gemini/"):
                model = f"gemini/{model}"
            self.model = model
            self.temperature = kwargs.get("temperature", 0.7)

        async def generate_content(self, prompt: str) -> str:
            if not acompletion:
                logger.warning("litellm is not installed. Returning empty JSON stub.")
                return "{}"
            
            try:
                response = await acompletion(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"LLM Generation Error: {str(e)}")
                raise e

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

    def __init__(self, config: Dict[str, Any], mock_infrastructure: bool = False):
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
                MockStateStore, MockMessageBroker, MockVectorStore, 
                MockFileStorage, MockTelemetry, MockMCPServer
            )
            self.state_store = MockStateStore(self.config)
            self.message_broker = MockMessageBroker(self.config)
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
        self.app = FastAPI(title="BaseAgentChassis API")
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

    def run_local(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Boot the Uvicorn/FastAPI server to serve the chassis locally.
        This is a blocking call and should be the entry point for running the application.
        """
        try:
            import uvicorn
        except ImportError:
            raise RuntimeError("uvicorn is required to run the local server. Install with `pip install uvicorn`")
        
        # Attach the start method to FastAPI startup event
        @self.app.on_event("startup")
        async def startup_event():
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

        @self.app.get("/studio", response_class=HTMLResponse)
        async def get_studio():
            """Returns the Agent Studio UI."""
            return """
            <!DOCTYPE html>
            <html lang="en" class="dark">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Agent Studio</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script>
                    tailwind.config = {
                        darkMode: 'class',
                    }
                </script>
                <style>
                    /* Custom scrollbar for webkit */
                    ::-webkit-scrollbar { width: 8px; }
                    ::-webkit-scrollbar-track { background: #1f2937; }
                    ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
                    ::-webkit-scrollbar-thumb:hover { background: #6b7280; }
                </style>
            </head>
            <body class="bg-gray-900 text-gray-100 h-screen flex flex-col antialiased">
                
                <!-- Header -->
                <header class="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between shrink-0">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white shadow-lg">S</div>
                        <h1 class="text-xl font-semibold tracking-tight text-white">Agent Studio</h1>
                    </div>
                    <div class="text-sm text-gray-400 bg-gray-900 px-3 py-1 rounded-full border border-gray-700">v1.0</div>
                </header>

                <!-- Chat History -->
                <main id="chat-history" class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
                    <!-- Initial Welcome Message -->
                    <div class="flex gap-4">
                        <div class="w-8 h-8 bg-blue-600 rounded-full flex shrink-0 items-center justify-center font-bold text-white text-sm shadow">S</div>
                        <div class="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm p-4 max-w-[85%] shadow-sm text-gray-200 leading-relaxed">
                            Hello! I am your local mock agent. How can I help you today?
                        </div>
                    </div>
                </main>

                <!-- Loading Indicator (Hidden by default) -->
                <div id="loading-indicator" class="hidden px-6 pb-2 text-sm text-gray-400 flex items-center gap-2">
                    <svg class="animate-spin h-4 w-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Agent is typing...
                </div>

                <!-- Input Area -->
                <footer class="bg-gray-800 border-t border-gray-700 p-4 shrink-0">
                    <div class="max-w-4xl mx-auto">
                        <form id="chat-form" class="relative flex items-end gap-2 bg-gray-900 rounded-2xl border border-gray-700 p-2 shadow-inner focus-within:ring-1 focus-within:ring-blue-500 focus-within:border-blue-500 transition-all">
                            
                            <!-- File Upload Button -->
                            <label for="file-upload" class="cursor-pointer p-3 text-gray-400 hover:text-blue-400 transition-colors rounded-xl hover:bg-gray-800 shrink-0 group">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 group-hover:scale-110 transition-transform">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
                                </svg>
                            </label>
                            <input id="file-upload" type="file" name="file" class="hidden" accept="*/*" />
                            
                            <!-- Display selected filename -->
                            <div id="file-name-display" class="hidden absolute -top-8 left-4 text-xs bg-blue-900 text-blue-200 px-3 py-1 rounded-full flex items-center gap-2 border border-blue-700 shadow-sm">
                                <span id="file-name-text" class="truncate max-w-[200px]"></span>
                                <button type="button" id="remove-file" class="hover:text-white">&times;</button>
                            </div>

                            <!-- Text Input -->
                            <textarea id="chat-input" name="message" rows="1" class="w-full bg-transparent text-gray-100 placeholder-gray-500 border-none focus:ring-0 resize-none py-3 px-2 text-[15px] leading-relaxed" placeholder="Type a message..."></textarea>
                            
                            <!-- Submit Button -->
                            <button type="submit" class="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0 shadow-md">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                                </svg>
                            </button>
                        </form>
                        <div class="text-center mt-3 text-xs text-gray-500">
                            Running on BaseAgentChassis • Mock Infrastructure
                        </div>
                    </div>
                </footer>

                <script>
                    const form = document.getElementById('chat-form');
                    const input = document.getElementById('chat-input');
                    const history = document.getElementById('chat-history');
                    const loading = document.getElementById('loading-indicator');
                    const fileUpload = document.getElementById('file-upload');
                    const fileNameDisplay = document.getElementById('file-name-display');
                    const fileNameText = document.getElementById('file-name-text');
                    const removeFileBtn = document.getElementById('remove-file');

                    // Auto-resize textarea
                    input.addEventListener('input', function() {
                        this.style.height = 'auto';
                        this.style.height = (this.scrollHeight < 120 ? this.scrollHeight : 120) + 'px';
                    });

                    // Handle Enter to submit (Shift+Enter for newline)
                    input.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            form.dispatchEvent(new Event('submit'));
                        }
                    });

                    // File upload UI handling
                    fileUpload.addEventListener('change', function() {
                        if (this.files && this.files[0]) {
                            fileNameText.textContent = this.files[0].name;
                            fileNameDisplay.classList.remove('hidden');
                        } else {
                            fileNameDisplay.classList.add('hidden');
                        }
                    });

                    removeFileBtn.addEventListener('click', function() {
                        fileUpload.value = '';
                        fileNameDisplay.classList.add('hidden');
                    });

                    // Basic Markdown Link Parser
                    function parseMarkdownLinks(text) {
                        // Parses [Text](URL) into <a href="URL" class="text-blue-400 hover:underline">Text</a>
                        return text.replace(/\\[(.*?)\\]\\((.*?)\\)/g, '<a href="$2" class="text-blue-400 hover:text-blue-300 font-medium underline decoration-blue-500/30 underline-offset-4" target="_blank">$1</a>');
                    }

                    // Append a message to the UI
                    function appendMessage(text, isUser = false, fileName = null) {
                        const div = document.createElement('div');
                        div.className = "flex gap-4 " + (isUser ? "flex-row-reverse" : "");
                        
                        let avatar = isUser 
                            ? `<div class="w-8 h-8 bg-gray-700 border border-gray-600 rounded-full flex shrink-0 items-center justify-center text-gray-300 text-sm shadow">U</div>`
                            : `<div class="w-8 h-8 bg-blue-600 rounded-full flex shrink-0 items-center justify-center font-bold text-white text-sm shadow">S</div>`;
                            
                        let bubbleClass = isUser
                            ? "bg-blue-600 text-white border-blue-500 rounded-tr-sm"
                            : "bg-gray-800 text-gray-200 border-gray-700 rounded-tl-sm";

                        let fileAttachmentHtml = fileName ? `
                            <div class="flex items-center gap-2 mb-2 p-2 rounded-lg bg-black/20 border border-black/10 text-sm">
                                <span>📎</span> <span class="truncate opacity-90">${fileName}</span>
                            </div>
                        ` : "";

                        // Parse markdown for agent messages
                        let contentHtml = isUser ? text.replace(/\\n/g, '<br>') : parseMarkdownLinks(text.replace(/\\n/g, '<br>'));

                        div.innerHTML = `
                            ${avatar}
                            <div class="border rounded-2xl p-4 max-w-[85%] shadow-sm leading-relaxed ${bubbleClass}">
                                ${fileAttachmentHtml}
                                <div>${contentHtml}</div>
                            </div>
                        `;
                        history.appendChild(div);
                        history.scrollTop = history.scrollHeight;
                    }

                    form.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const message = input.value.trim();
                        const file = fileUpload.files[0];
                        
                        if (!message && !file) return;

                        // UI Updates
                        appendMessage(message || "(File Upload)", true, file ? file.name : null);
                        input.value = '';
                        input.style.height = 'auto';
                        fileUpload.value = '';
                        fileNameDisplay.classList.add('hidden');
                        loading.classList.remove('hidden');

                        try {
                            const formData = new FormData();
                            if (message) formData.append('message', message);
                            if (file) formData.append('file', file);
                            formData.append('user_id', 'studio_user');
                            formData.append('session_id', 'studio_session');
                            formData.append('tenant_id', 'local_dev');

                            const response = await fetch('/chat', {
                                method: 'POST',
                                body: formData
                            });

                            if (!response.ok) throw new Error("Server Error");
                            
                            const data = await response.json();
                            appendMessage(data.response || "Task completed.");

                        } catch (err) {
                            appendMessage("⚠️ Error communicating with agent.", false);
                        } finally {
                            loading.classList.add('hidden');
                        }
                    });
                </script>
            </body>
            </html>
            """

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
            
            # In a real sync scenario, we would need a way to await the result of the specific queue.
            # Because decorators are async while True loops, the easiest way to test in Studio
            # is to publish to the default queue and read from a generic response queue, or 
            # execute the underlying logic directly. 
            
            # For the mock Studio UI, we'll return a simulated response if we detect the HelloRequest model.
            try:
                # Let's try to simulate processing for 'hello_jobs'
                context = AgentContext(user_id=user_id, session_id=session_id, tenant_id=tenant_id)
                
                # We'll publish the message to the first available queue to kick off the background worker
                # (which was started in `start()`), but we won't wait for it since it's fire-and-forget.
                # However, for a chat UI, users expect a synchronous reply.
                # So we will invoke the LLM directly for the UI preview.
                
                prompt = f"User said: {message}"
                if file_id:
                    prompt += f" [Attached File ID: {file_id}]"
                    
                response_text = await self.llm_agent.generate_content(prompt)
                return {"response": response_text}
                
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
            self._consumers.append(wrapper)
            return wrapper
        return decorator
