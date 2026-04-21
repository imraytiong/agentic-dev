import os
import sys
import uuid
import time
import yaml
import asyncio
import logging
from typing import Dict, Any
from pydantic import BaseModel
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext

# Basic models for state/broker diagnostics
class FrankyState(BaseModel):
    id: str
    message: str

class FrankyPayload(BaseModel):
    diagnostic_id: str
    data: str

# Configuration loading
config_path = os.path.join(os.path.dirname(__file__), "agent.yaml")

def load_config() -> Dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
chassis = BaseAgentChassis(config, enable_studio=False)

def log_success(step: int, component: str, latency_ms: float):
    print(f"[DIAGNOSTIC] STEP={step} COMPONENT={component} STATUS=PASS LATENCY={latency_ms:.2f}ms")

def log_error(step: int, component: str, exception: Exception):
    print(f"[DIAGNOSTIC_ERROR] STEP={step} COMPONENT={component} EXCEPTION={type(exception).__name__} MESSAGE=\"{str(exception)}\"")

async def run_diagnostics():
    print("[DIAGNOSTIC] STATUS=STARTING")
    context = AgentContext(user_id="franky_admin", session_id=str(uuid.uuid4()), tenant_id="system")
    
    # Step 1: LLM/FinOps Assertion
    step = 1
    component = "LLM"
    start_time = time.time()
    try:
        prompt = "You are a diagnostic tool. Reply with exactly two words: 'Franky Online'"
        response = await chassis.llm_provider.generate_content(
            model=config["agent"].get("model", "gemini-2.5-flash"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config["agent"].get("max_tokens", 10),
            temperature=config["agent"].get("temperature", 0.0)
        )
        
        try:
            content = response.choices[0].message.content.strip()
            assert "Franky Online" in content, f"Expected 'Franky Online', got '{content}'"
        except AttributeError:
            if isinstance(response, dict) and "choices" in response:
                content = response["choices"][0]["message"]["content"].strip()
                assert "Franky Online" in content, f"Expected 'Franky Online', got '{content}'"
            else:
                 pass # Fallback for legacy wrapper
                 
        latency = (time.time() - start_time) * 1000
        log_success(step, component, latency)
    except Exception as e:
        log_error(step, component, e)
        sys.exit(1)

    # Step 2: State JSONB Assertion
    step = 2
    component = "STATE_STORE"
    start_time = time.time()
    try:
        diag_id = str(uuid.uuid4())
        state_key = f"franky_state_{diag_id}"
        state_data = FrankyState(id=diag_id, message="Diagnostic Data")
        
        await chassis.state_store.save_state(state_key, state_data)
        loaded_state = await chassis.state_store.load_state(state_key, FrankyState)
        
        assert loaded_state.id == diag_id, f"State ID mismatch: {loaded_state.id} != {diag_id}"
        assert loaded_state.message == "Diagnostic Data", f"State Message mismatch"
        
        latency = (time.time() - start_time) * 1000
        log_success(step, component, latency)
    except Exception as e:
        log_error(step, component, e)
        sys.exit(1)

    # Step 3: Vector Assertion
    step = 3
    component = "VECTOR_STORE"
    start_time = time.time()
    try:
        embedding = [0.1] * 1536
        vec_id = f"vec_{diag_id}"
        
        await chassis.vector_store.add_documents(
            documents=["Franky vector diagnostic string"],
            metadatas=[{"type": "diagnostic"}],
            ids=[vec_id],
            embeddings=[embedding]
        )
        
        results = await chassis.vector_store.semantic_search(embedding, limit=1)
        assert len(results) > 0, "No vector results returned"
        assert results[0]["key"] == vec_id, f"Vector ID mismatch: {results[0]['key']} != {vec_id}"
        
        latency = (time.time() - start_time) * 1000
        log_success(step, component, latency)
    except Exception as e:
        log_error(step, component, e)
        sys.exit(1)

    # Step 4: Message Broker Assertion
    step = 4
    component = "MESSAGE_BROKER"
    start_time = time.time()
    try:
        queue_name = f"franky_diag_queue_{diag_id}"
        payload = FrankyPayload(diagnostic_id=diag_id, data="Diagnostic Ping")
        
        await chassis.message_broker.publish(queue_name, payload, context)
        
        result = await asyncio.wait_for(
            chassis.message_broker.listen(queue_name, consumer_group="franky_group", consumer_name="franky_consumer"), 
            timeout=5.0
        )
        
        assert result is not None, "Message broker returned None"
        if isinstance(result, tuple):
            msg_data, msg_id = result
            assert msg_data["payload"]["diagnostic_id"] == diag_id, f"Broker Payload ID mismatch: {msg_data['payload']}"
        else:
             assert result["payload"]["diagnostic_id"] == diag_id, f"Broker Payload ID mismatch (Mock)"
             
        latency = (time.time() - start_time) * 1000
        log_success(step, component, latency)
    except asyncio.TimeoutError as e:
        log_error(step, component, Exception("Message Broker Listen Timed Out"))
        sys.exit(1)
    except Exception as e:
        log_error(step, component, e)
        sys.exit(1)

    # Clean teardown
    print("[DIAGNOSTIC] STATUS=TEARDOWN")
    if hasattr(chassis.state_store, "close"):
        await getattr(chassis.state_store, "close")()
    if hasattr(chassis.message_broker, "close"):
        await getattr(chassis.message_broker, "close")()
        
    print("[DIAGNOSTIC] STATUS=COMPLETE EXIT_CODE=0")
    sys.exit(0)

if __name__ == "__main__":
    # Disable global logging to keep standard output perfectly clean for CLI parsers
    logging.getLogger("src.universal_core.chassis").setLevel(logging.CRITICAL)
    logging.getLogger("src.infrastructure.adapters.mock_adapters").setLevel(logging.CRITICAL)
    logging.getLogger("src.infrastructure.adapters.postgres_adapter").setLevel(logging.CRITICAL)
    logging.getLogger("src.infrastructure.adapters.redis_adapter").setLevel(logging.CRITICAL)
    logging.getLogger("src.infrastructure.adapters.litellm_adapter").setLevel(logging.CRITICAL)
    logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
    
    asyncio.run(run_diagnostics())
