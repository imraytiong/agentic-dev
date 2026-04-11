import logging
import os
from typing import Dict, Any
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from .models import HelloRequest, HelloState, HelloResponse
from .tools import get_affirmation
import yaml

logger = logging.getLogger(__name__)

# Assuming config is loaded from the agent's directory for local dev
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config() -> Dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
chassis = BaseAgentChassis(config)

@chassis.consume_task(queue_name="hello_jobs", payload_model=HelloRequest)
async def process_hello(payload: HelloRequest, context: AgentContext):
    """
    The main execution loop for the Sparky agent.
    """
    logger.info(f"Sparky is greeting {payload.developer_name}")
    
    # 1. Load State
    state_key = f"sparky_state_{context.user_id}"
    try:
        state = await chassis.state_store.load_state(state_key, HelloState)
    except Exception as e:
        logger.warning(f"Failed to load state, initializing new: {e}")
        state = HelloState()
        
    # 2. Update State
    state.interaction_count += 1
    
    # 3. Use Tools
    affirmation = get_affirmation(payload.current_mood)
    
    # 4. Execute Task via LLM 
    # (Loading prompt template - assuming it will be in the prompts directory created in Layer 5)
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.jinja")
    template_str = ""
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            template_str = f.read()
    else:
        # Fallback template if file doesn't exist yet
        template_str = "Say hello to {{ developer_name }} who is feeling {{ current_mood }}. Include this affirmation: {{ affirmation }}. Current interactions: {{ count }}"
        
    template_vars = {
        "developer_name": payload.developer_name,
        "current_mood": payload.current_mood,
        "affirmation": affirmation,
        "count": state.interaction_count
    }
    
    response = await chassis.execute_task(
        template_str=template_str,
        template_vars=template_vars,
        response_model=HelloResponse,
        context=context
    )
    
    # 5. Save State
    await chassis.state_store.save_state(state_key, state)
    
    # Override total_interactions in the LLM response to ensure accuracy
    response.total_interactions = state.interaction_count
    
    return response

if __name__ == "__main__":
    # Boot the local mock harness
    logging.basicConfig(level=logging.INFO)
    chassis.run_local()
