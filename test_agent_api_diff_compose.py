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
    print("🚀 API Diff Trace: Compose UI & Navigation...\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    from src.universal_core.mock_adapters import MockVectorStore, MockStateStore
    chassis.vector_store = MockVectorStore()
    chassis.state_store = MockStateStore(config)
    
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="trace_user_diff2", session_id="trace_session_diff2", tenant_id="local_dev")

    # TEST 1: Compose UI Geometry
    print("--------------------------------------------------------------------------")
    print("🗣️  TEST 1: Compose UI Geometry")
    print("--------------------------------------------------------------------------")
    state_key = f"jetpack_wiz_state_{context.session_id}"
    from src.agents.jetpack_wiz.models import JetpackWizState, ActiveFocus
    state1 = JetpackWizState(has_indexed=True, active_focus=ActiveFocus(module_path="compose/ui/ui-geometry"))
    await chassis.state_store.save_state(state_key, state1)
    
    req1 = JetpackWizRequest(query="Compare the API changes between 1.0.0-beta02 and 1.10.0-beta01 for api/current.txt")
    res1 = await inner_func(req1, context)
    print(f"\n🤖 AGENT REPLY:\n{res1.message}\n")

    # TEST 2: Navigation UI
    print("--------------------------------------------------------------------------")
    print("🗣️  TEST 2: Navigation UI")
    print("--------------------------------------------------------------------------")
    state2 = JetpackWizState(has_indexed=True, active_focus=ActiveFocus(module_path="navigation/navigation-ui"))
    await chassis.state_store.save_state(state_key, state2)
    
    # We will simulate a query that requires finding the tags first, since 
    # the repo might not have simple tag names for navigation.
    req2 = JetpackWizRequest(query="What has changed since the last version?")
    res2 = await inner_func(req2, context)
    print(f"\n🤖 AGENT REPLY:\n{res2.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
