import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

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
    print("🚀 Forcing an API Diff Analysis Trace...\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    from src.universal_core.mock_adapters import MockVectorStore, MockStateStore
    chassis.vector_store = MockVectorStore()
    chassis.state_store = MockStateStore(config)
    
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="trace_user_force", session_id="trace_session_force", tenant_id="local_dev")

    # Pre-set focus
    state_key = f"jetpack_wiz_state_{context.session_id}"
    from src.agents.jetpack_wiz.models import JetpackWizState, ActiveFocus
    state = JetpackWizState(has_indexed=True, active_focus=ActiveFocus(module_path="appcompat/appcompat"))
    await chassis.state_store.save_state(state_key, state)

    # We skip discovery and go straight to the compare query
    print("🗣️  USER: 'Compare the API changes between support-library-27.1.0 and support-library-27.1.1 for appcompat/appcompat/api/current.txt'")
    
    req = JetpackWizRequest(query="Compare the API changes between support-library-27.1.0 and support-library-27.1.1 for appcompat/appcompat/api/current.txt")
    res = await inner_func(req, context)
    print(f"\n🤖 AGENT REPLY:\n{res.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
