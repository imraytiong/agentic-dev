import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.universal_core.chassis import BaseAgentChassis

@pytest.fixture
def chassis():
    config = {
        "agent": {
            "name": "TestAgent",
            "model": "gemini-1.5-flash",
            "system_prompt": "You are a test agent."
        },
        "infrastructure": {}
    }
    
    # Isolate OpenTelemetry global singleton using unittest.mock.patch
    with patch('src.universal_core.chassis.trace.get_tracer_provider') as mock_get_provider:
        from opentelemetry.sdk.trace import TracerProvider
        mock_provider = MagicMock(spec=TracerProvider)
        mock_get_provider.return_value = mock_provider
        
        # Initialize with enable_studio=True
        c = BaseAgentChassis(config, mock_infrastructure=True, enable_studio=True)
        yield c

@pytest.fixture
def client(chassis):
    return TestClient(chassis.app)

def test_studio_api_config(client):
    response = client.get("/studio/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gemini/gemini-1.5-flash"
    assert data["system_prompt"] == "You are a test agent."

def test_studio_api_logs(client, chassis):
    # Ensure the handler is capturing
    chassis.studio_log_handler.emit(logging.LogRecord(
        name="test", level=logging.DEBUG, pathname="test.py", lineno=1,
        msg="Debug message for studio", args=None, exc_info=None
    ))
    chassis.studio_log_handler.emit(logging.LogRecord(
        name="test", level=logging.INFO, pathname="test.py", lineno=2,
        msg="Info message for studio", args=None, exc_info=None
    ))
    
    response = client.get("/studio/api/logs")
    assert response.status_code == 200
    html = response.text
    assert "Debug message for studio" in html
    assert "Info message for studio" in html
    assert "text-gray-400" in html  # DEBUG color
    assert "text-blue-400" in html  # INFO color

def test_studio_api_telemetry_serialization(client, chassis):
    if not chassis.studio_span_exporter:
        pytest.skip("OTel not available")
        
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider, Span
    from opentelemetry.trace import SpanContext, TraceFlags
    
    # Create a mock span with specific IDs
    trace_id = 0xdeadbeefdeadbeefdeadbeefdeadbeef
    span_id = 0x1234567812345678
    
    span_context = SpanContext(
        trace_id=trace_id,
        span_id=span_id,
        is_remote=False,
        trace_flags=TraceFlags.SAMPLED,
    )
    
    # Manually create a FinishedSpan-like object or use the exporter's buffer
    class MockSpan:
        def __init__(self, name, tid, sid):
            self.name = name
            self.context = type('obj', (object,), {'trace_id': tid, 'span_id': sid})
            self.start_time = 1000000000
            self.end_time = 1050000000  # 50ms duration
            self.attributes = {"key": "value"}
            self.status = type('obj', (object,), {'is_ok': True})
            
    chassis.studio_span_exporter.get_finished_spans = lambda: [MockSpan("LLM Generate", trace_id, span_id)]
    
    response = client.get("/studio/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["trace_id"] == "deadbeefdeadbeefdeadbeefdeadbeef"
    assert data[0]["span_id"] == "1234567812345678"
    assert data[0]["type"] == "llm"
    assert data[0]["duration_ms"] == 50.0

def test_studio_ui_page(client):
    response = client.get("/studio")
    assert response.status_code == 200
    assert "Agent Studio: TestAgent" in response.text
    assert "data-testid=\"telemetry-panel\"" in response.text
    assert "data-testid=\"live-logs-container\"" in response.text

def test_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/studio"

def test_studio_disabled(chassis):
    chassis.enable_studio = False
    client = TestClient(chassis.app)
    
    # Config should return empty dict
    assert client.get("/studio/api/config").json() == {}
    
    # UI should return 404
    assert client.get("/studio").status_code == 404
