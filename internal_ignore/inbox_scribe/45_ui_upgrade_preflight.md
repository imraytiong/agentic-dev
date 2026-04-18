# Pre-flight Plan: UI Upgrade for Agent Studio

**Objective:** Transform the Agent Studio UI into a comprehensive Developer Dashboard as per Spec 44.

**Proposed Branch:** `track/ui-upgrade-studio-20260418`

## Strategy
1. **Extraction**: Move the current embedded HTML in `chassis.py` to `src/universal_core/studio.html`.
2. **Infrastructure Enhancement**:
   - Add `MemoryLogHandler` (deque-based) to capture DEBUG logs for the UI.
   - Integrate `InMemorySpanExporter` for OTel telemetry without breaking existing pipelines.
   - Add `enable_studio` toggle and `quiet` flag support.
3. **API Implementation**:
   - `GET /studio/api/config` (JSON)
   - `GET /studio/api/telemetry` (JSON, serialized OTel spans)
   - `GET /studio/api/logs` (HTML fragments for HTMX)
   - `GET /` redirect to `/studio`.
4. **UI Revamp**:
   - Implement split-pane layout with Tailwind CSS.
   - Use Alpine.js for state management (collapsibles, polling).
   - Use HTMX for live log updates.
   - Add `data-testid` for testability.
5. **Testing**:
   - Unit tests for new Studio API endpoints.
   - Regression testing of existing chassis functionality.

## Verification Strategy
- **Manual Verification**: Boot the chassis and inspect the dashboard.
- **Automated Tests**: Assert JSON structure of telemetry and config APIs. Assert HTML fragment structure of log API.
