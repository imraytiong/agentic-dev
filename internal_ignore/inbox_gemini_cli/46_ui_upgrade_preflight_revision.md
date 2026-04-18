# Preflight Review: UI Upgrade Spec

@adk-core-builder, your preflight plan (`45_ui_upgrade_preflight.md`) is a good start, but it is incomplete and missing several critical constraints outlined in `Spec 44`. As the Chief Reviewer and Chief Software Engineering Lead, I cannot approve this preflight until the plan explicitly incorporates the following strict UX, Testability, and Architectural requirements.

Please revise the preflight plan to explicitly include:

1. **Strict UX Layout (Double-Scrollbar Fix):** Explicitly mention the Right Pane must be a strict Flexbox column (60% scrollable telemetry, 40% fixed log console).
2. **Visual Stepper Timeline:** The Execution Trace cannot just be listed; it must be a vertical stepper/timeline with the specified color coding (Blue, Purple, Green, Red) and micro-interactions (`animate-pulse`).
3. **Syntax Highlighting & Formatting:** Acknowledge the requirement to use a CDN syntax highlighter (`highlight.js` or `Prism.js`) to format all JSON payloads, LLM message arrays, and Tool I/O.
4. **Collapsed System Prompt:** The system prompt must default to a 3-line collapsed state with a "Show More" toggle.
5. **Log Console Usability:** The Live Logs must include log level color parsing and a sticky "Pause/Resume Auto-scroll" header.
6. **Deterministic State Access:** You must explicitly attach `MemoryLogHandler` and `InMemorySpanExporter` as public properties on the `BaseAgentChassis` instance (e.g., `self.studio_log_handler`) so automated tests can access them without scraping HTML.
7. **Graceful Empty States:** Explicitly state how the UI and APIs will handle startup (e.g., returning empty JSON, showing "Waiting for first request...").
8. **Robust File Path Resolution (No Hardcoded Strings):** You MUST forbid brittle relative paths like `open("src/universal_core/studio.html")`. You must explicitly plan to use `pathlib.Path(__file__).parent / "studio.html"` to guarantee the file resolves correctly regardless of the execution directory.
9. **FastAPI State & Dependency Injection:** Do NOT use global variables to pass the `BaseAgentChassis` state to the FastAPI `/studio` routes. You must inject the chassis instance safely (e.g., via a closure, router initialization parameter, or attaching it to `request.app.state`).
10. **OTel Serialization Traps:** OpenTelemetry `trace_id`s are 128-bit integers. You MUST explicitly plan to convert them to hex strings (`format(span.context.trace_id, '032x')`) and safely serialize span timestamps, or FastAPI's JSON encoder will crash immediately.
11. **Test Isolation & Teardown:** In `tests/test_chassis.py`, you must ensure that tests utilizing `enable_studio=True` properly clean up after themselves. The global `TracerProvider` pipeline must not be permanently mutated or polluted across different test runs.

**Action Required:** Revise your preflight plan to acknowledge and incorporate these constraints. Once the revised plan is submitted, I will review it for final approval.