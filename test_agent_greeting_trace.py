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

logging.basicConfig(level=logging.ERROR, format='%(message)s')

async def main():
    print("\n==========================================================================")
    print("🚀  JETPACKWIZ AGENT - GREETING & CAPABILITIES TRACE TEST 🚀")
    print("==========================================================================\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    from src.universal_core.mock_adapters import MockVectorStore, MockStateStore
    chassis.vector_store = MockVectorStore()
    chassis.state_store = MockStateStore(config)
    
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="trace_user_greet", session_id="trace_session_greet", tenant_id="local_dev")

    # Force re-index (silently) to simulate a ready environment
    req_init = JetpackWizRequest(query="init")
    await inner_func(req_init, context)
    print("✅ System Initialized. Repository is ready.\n")

    print("--------------------------------------------------------------------------")
    print("🗣️  USER: 'Hello there!'")
    print("--------------------------------------------------------------------------")
    
    # We expect the agent to intercept this greeting directly and return the capabilities
    req = JetpackWizRequest(query="Hello there!")
    res = await inner_func(req, context)
    print(f"🤖 AGENT REPLY:\n{res.message}\n")
    print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())
