# Pre-flight Plan: UI Upgrade for Agent Studio (REVISED)

**Objective:** Transform the Agent Studio UI into a comprehensive Developer Dashboard as per Spec 44.

**Proposed Branch:** `track/ui-upgrade-studio-20260418`

## Strategy
1. **Extraction & Robust Resolution**:
   - Move embedded HTML to `src/universal_core/studio.html`.
   - **Constraint**: Use `pathlib.Path(__file__).parent / "studio.html"` for resolution to avoid brittle paths.
2. **Infrastructure Enhancement**:
   - Add `MemoryLogHandler` (deque maxlen=100) and `InMemorySpanExporter`.
   - **Constraint**: Attach these as public properties (e.g., `self.studio_log_handler`, `self.studio_span_exporter`) for deterministic state access by automated tests.
   - Implement `enable_studio` toggle (default False) and CLI `--quiet` flag support.
   - Ensure `MemoryLogHandler` always captures `DEBUG` even if CLI is `--quiet`.
3. **API Implementation (FastAPI State Injection)**:
   - **Constraint**: Inject chassis state into routes via `request.app.state` (no globals).
   - `GET /studio/api/config`: Dynamic JSON reading from chassis properties.
   - `GET /studio/api/telemetry`: JSON serialization of OTel spans.
     - **Constraint**: Convert `trace_id` to hex strings (`032x`) and safely serialize timestamps to avoid JSON encoder crashes.
     - **Constraint**: Implement a rolling buffer/filter for spans to ensure concurrency safety (do NOT use `.clear()`).
   - `GET /studio/api/logs`: HTML fragments (polled via HTMX) with log level color parsing (Tailwind: DEBUG/gray, INFO/blue, WARN/yellow, ERROR/red).
   - `GET /` redirect to `/studio`.
4. **UI Revamp (UX & Accessibility)**:
   - **Constraint**: Split-pane layout with Right Pane as a strict Flexbox column (60% scrollable telemetry, 40% fixed log console) to prevent the "Double Scrollbar" trap.
   - **Constraint**: Execution Trace styled as a vertical stepper/timeline with specified color coding (Blue/Purple/Green/Red) and `animate-pulse` for active states.
   - **Constraint**: Integrate CDN syntax highlighter (`highlight.js`) for all JSON, LLM message arrays, and Tool I/O.
   - **Constraint**: System Prompt collapsed by default (first 3 lines) with a "Show More" toggle via Alpine.js.
   - **Constraint**: Sticky "Pause/Resume Auto-scroll" header in the Live Logs console.
   - **Constraint**: Graceful empty states (e.g., "Waiting for first request...") and valid empty JSON responses on startup.
   - Use Alpine.js for state management and HTMX for polling. Include `data-testid` on all critical elements.
5. **Testing & Isolation**:
   - Unit tests for all `/studio/api/*` endpoints.
   - **Constraint**: Ensure test isolation in `tests/test_chassis.py`. Properly teardown `enable_studio=True` states and avoid polluting the global `TracerProvider` across test runs.

## Verification Strategy
- **Manual Verification**: Boot the chassis and inspect the dashboard layout, syntax highlighting, and log color coding.
- **Automated Tests**: Assert JSON serialization of OTel spans (hex IDs). Assert HTML fragment structure for logs. Verify deterministic access via `chassis.studio_log_handler`.
