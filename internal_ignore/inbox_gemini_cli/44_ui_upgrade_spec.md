# UI Upgrade Spec: Agent Studio Developer Tools

## Objective
Transform the Agent Studio UI from a simple chat interface into a comprehensive "Developer Dashboard" for Agent-Driven Development. This upgrade will expose the internal state, telemetry, and execution traces of the agent directly in the browser.

## Instructions for Gemini CLI (@adk-core-builder)

This specification outlines upgrades to the Universal Core. **Do not implement infrastructure adapters.** Stay within the boundaries of the `BaseAgentChassis` and strictly follow these architectural constraints to prevent brittle code or DOM vulnerabilities.

### 1. Architectural Constraints & Safety Rails (CRITICAL)
- **Mock Mode First (Lightweight Constraint):** The Studio UI's primary use case is when a developer is running the agent in Mock Mode locally. Therefore, it **MUST remain extremely lightweight**. Do not introduce any heavyweight backend dependencies (e.g., WebSockets, Redis, Celery) or complex frontend build steps (e.g., React, NPM, Webpack). 
- **Explicit CDN Imports:** Rely entirely on CDN-delivered frontend libraries. In the `<head>`, include standard CDN links for Tailwind CSS (via script tag), Alpine.js, HTMX, and a lightweight syntax highlighter like `highlight.js` or `Prism.js`.
- **HTML Extraction:** Do not bloat `chassis.py` with massive HTML strings. Extract the HTML template into a new file: `src/universal_core/studio.html`. Have `chassis.py` read this file on startup.
- **UI Layout (Split-Pane & Flexbox):** Use a strict, static CSS Grid (e.g., `grid-cols-1 md:grid-cols-2`). 
  - **Left Pane:** Preserve the existing chat interface functionality.
  - **Right Pane:** The new Developer Dashboard. To avoid the "Double Scrollbar" trap, this must be a strict Flexbox column. 
    - The **top 60%** must be a scrollable area housing the Configuration, Execution Trace, and Adapters sections.
    - The **bottom 40%** must be a fixed-height, independently scrolling Live Log console pinned to the bottom.
- **DOM Isolation (Polling):** Ensure that the HTMX and Alpine.js polling intervals are strictly scoped to elements within the *Right Pane*. Polling must not trigger DOM refreshes or steal focus from the Chat input box in the *Left Pane*.
- **Data Flow & API Namespacing:** Do not multiplex SSE on the `/chat` endpoint. Implement a clean polling mechanism, and strictly namespace UI endpoints to avoid API pollution:
  - Create a `GET /studio/api/telemetry` endpoint returning **JSON** (polled via Alpine.js `setInterval`) for structured trace data.
  - Create a `GET /studio/api/logs` endpoint returning **HTML fragments** (polled via HTMX `hx-trigger="every 2s"`) for raw log lines.
  - Create a `GET /studio/api/config` endpoint returning **JSON** for configuration state.
- **Telemetry Integration (OpenTelemetry):** You must wrap an **`InMemorySpanExporter`** (from `opentelemetry.sdk.trace.export`) inside a `SimpleSpanProcessor` and add that processor to the existing `TracerProvider` configured by the ADK's `_setup_telemetry()` step. Do not overwrite the existing pipeline.
  - *Serialization Warning:* OTel spans are complex Python objects and are NOT natively JSON serializable. In the `GET /studio/api/telemetry` endpoint, you MUST manually extract and serialize the `.name`, `.attributes`, and `.events` properties into standard Python dictionaries before returning them.
  - *Concurrency Safety:* Do NOT call `.clear()` on the global `InMemorySpanExporter`. FastAPI is asynchronous, and clearing global state will break concurrent requests. Instead, have the UI filter spans by the `trace_id` returned by the `/chat` request, or implement a rolling buffer (e.g., only returning the last 500 spans).
- **Live Logs Integration:** Do not overwrite `sys.stdout` or use blocking threads. Implement a custom Python `logging.Handler` (e.g., `MemoryLogHandler`) that appends to a `collections.deque(maxlen=100)`.
- **XSS, Formatting & Syntax Highlighting:** All raw text, JSON, and Jinja templates MUST be rendered safely. Use the CDN syntax highlighter (`highlight.js`/`Prism.js`) to format JSON payloads, LLM message arrays, and Tool outputs. Wrap large payloads in an Alpine.js toggle to collapse/expand them. In Alpine.js, strictly use `x-text` (never `x-html`) to prevent `<system>` tags or prompt injections from breaking the DOM.

### 2. Root Path Routing
- Add a route so that the root path (`GET /`) automatically serves or redirects to the `/studio` interface, preserving any dynamic template variables like `__AGENT_NAME__`.

### 3. Agent DevTools Sections (Right Pane)

#### Section A: Configuration
- **Dynamic Config Access:** The `GET /studio/api/config` endpoint must dynamically read these values from the `BaseAgentChassis` instance properties at runtime.
- **System Prompt (Information Hierarchy):** Show the raw Jinja template being used. **UX Requirement:** It must default to a *collapsed* state, showing only the first 3 lines with a faded CSS gradient and a "Show More" button (toggled via Alpine.js) to prevent a "wall of text".
- **Model:** Show the active LLM model.
- **Tools:** List the tools registered and available to the agent.

#### Section B: Execution Trace (Visual Timeline)
- Provide a timeline of the request lifecycle by parsing the OTel spans. 
- **UX Requirement:** This MUST be styled using Tailwind as a **vertical stepper/timeline**. Use clear iconography and color coding: User Input (Blue), LLM Reasoning/Generation (Purple), Tool Execution (Green), Errors (Red). Connect nodes with a visual line.
- **Micro-Interactions:** When the HTMX poll is active or the chat request is pending, show a subtle CSS pulse animation (e.g., Tailwind's `animate-pulse`) on the current active step in the timeline.
- Timeline Steps:
  1. Receiving and parsing the user prompt.
  2. The LiteLLM message array payload sent to the LLM. Must be properly parsed, syntax-highlighted, and formatted from the span attributes. 
  3. Tool calls (displaying exact JSON inputs and outputs, syntax-highlighted and collapsible).
  4. The final generated response to the user.

#### Section C: Adapters & Skills
- **Skills:** List which agent skills were loaded into the current context.
- **Backend Mock Adapters:** Trace interactions with the Mock Infrastructure engine:
  - *VectorStore (ChromaDB):* Display queries made and retrieved chunks.
  - *Memory/State:* Display read/writes to the session memory.

#### Section D: Live Logs (Independent Console)
- Implement a live scrolling log viewer box displaying the contents of the `MemoryLogHandler` via the `/studio/api/logs` endpoint.
- **UX Requirement (Layout):** This must occupy the bottom 40% of the Right Pane as a fixed-height, independently scrolling container.
- **UX Requirement (Usability):** 
  - Parse log levels and apply Tailwind text colors: DEBUG = `text-gray-400`, INFO = `text-blue-400`, WARN = `text-yellow-400`, ERROR = `text-red-500 font-bold`.
  - Include a sticky header with a "Pause/Resume Auto-scroll" toggle button (using Alpine.js to halt the HTMX polling or scrolling behavior) so developers can read errors before they vanish.

### 4. Logging & CLI Verbosity (Mock Mode)
To ensure the codelab participants can see what is happening "under the hood" and to allow the AI end-to-end testing skill to parse execution state, implement the following logging behavior:

- **Default Behavior (Verbose/DEBUG):** By default, running the agent locally MUST output highly detailed logs to the console.
  - *What to log:* Server startup, mock adapters initialized, skills loaded, incoming HTTP requests, raw user prompts, structured LiteLLM message arrays, exact JSON inputs/outputs for tools, mock infrastructure queries (e.g., ChromaDB semantic searches), and routing/queue handoffs.
- **The `--quiet` Flag:** Add standard CLI argument parsing (e.g., via `argparse` in the agent's entry point or `BaseAgentChassis.run()`) to accept a `--quiet` or `-q` flag.
  - *Behavior when enabled:* The console output is reduced to `INFO` / `WARNING` levels (e.g., startup banner, port info, basic access logs, and errors). All payload dumps, tool I/O, and LLM reasoning traces are suppressed from the console.
- **Dual Handler Architecture:** 
  - The standard Console Handler (`StreamHandler`) will respect the `--quiet` flag (toggling between `DEBUG` and `INFO`).
  - The UI's `MemoryLogHandler` (which feeds the Agent Studio Live Logs tab) MUST ALWAYS capture `DEBUG` logs. This ensures the web dashboard remains fully populated with detailed traces even if the terminal is running in quiet mode.

### 5. Testability & Production Resilience (CRITICAL)
To ensure our Agent-Driven Development loop remains robust and testable without human intervention:

- **Semantic Testability (The `data-testid` Mandate):** Explicitly mandate the use of `data-testid` attributes on all critical DOM elements in `studio.html` (e.g., `data-testid="live-logs"`, `data-testid="trace-step"`, `data-testid="config-model"`). This ensures our E2E testing skill can reliably assert UI state without relying on brittle CSS classes.
- **Unit Testing the Studio APIs:** Write explicit `pytest` unit tests for the new endpoints (`/studio/api/config`, `/studio/api/telemetry`, `/studio/api/logs`) in `tests/test_chassis.py` (or the relevant core test file). Mock the `BaseAgentChassis` state and assert the JSON contracts and HTML fragment generation.
- **The "Production Kill Switch" (Safe Defaults Protocol):** The `BaseAgentChassis` must accept an `enable_studio: bool = False` parameter (or read an environment variable). The `/studio` routes, `MemoryLogHandler`, and `InMemorySpanExporter` should *only* be mounted and attached if this flag is `True`.
- **Deterministic State Access for the AI Tester:** Attach the `MemoryLogHandler` and the `InMemorySpanExporter` as public properties on the `BaseAgentChassis` instance (e.g., `self.studio_log_handler`, `self.studio_span_exporter`). This allows automated test scripts to directly assert against internal buffers (e.g., `chassis.studio_log_handler.buffer`) to verify logic without scraping HTML.
- **Graceful Empty States (The Startup Crash):** Ensure graceful handling of empty states when the server first boots. The `/studio/api/telemetry` endpoint must return a valid, empty JSON structure if no traces exist. The UI must display a polite "Waiting for first request..." placeholder instead of breaking or throwing errors.