import asyncio
import logging
import json
import os
import yaml

os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")

from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from src.agents.jetpack_wiz.agent import register_jetpack_wiz_agent
from src.agents.jetpack_wiz.models import JetpackWizRequest

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    print("🚀 Testing Autonomous API Discovery (General Query)...\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    from src.universal_core.mock_adapters import MockVectorStore, MockStateStore
    chassis.vector_store = MockVectorStore()
    chassis.state_store = MockStateStore(config)
    
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="auto_api_user", session_id="auto_api_session", tenant_id="local_dev")

    # Step 1: Pre-set the focus to compose/ui to simulate a mid-conversation state
    state_key = f"jetpack_wiz_state_{context.session_id}"
    from src.agents.jetpack_wiz.models import JetpackWizState, ActiveFocus
    state = JetpackWizState(
        has_indexed=True, 
        active_focus=ActiveFocus(module_path="compose/ui")
    )
    await chassis.state_store.save_state(state_key, state)

    # Step 2: Ask the general query
    print("==================================================")
    print("🗣️  USER: list the public apis available for the modules here")
    print("==================================================")
    req = JetpackWizRequest(query="list the public apis available for the modules here")
    res = await inner_func(req, context)
    print(f"\n🤖 AGENT REPLY:\n{res.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
