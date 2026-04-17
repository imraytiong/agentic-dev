import asyncio
import logging
import json
import os
import yaml

# Use litellm with Gemini API key from the environment
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")

from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from src.agents.jetpack_wiz.agent import register_jetpack_wiz_agent
from src.agents.jetpack_wiz.models import JetpackWizRequest

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    print("🚀 Starting LIVE test of the JetpackWiz Agent routing loop (with REAL GEMINI LLM)...\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # We use mock_infrastructure=False to actually hit the LLM via litellm/google_adk
    # But we patch the vector store so we don't need a real Postgres/Redis instance running for the test
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    
    # Force mock vector/state stores for this specific test
    from src.universal_core.mock_adapters import MockVectorStore, MockStateStore
    chassis.vector_store = MockVectorStore()
    chassis.state_store = MockStateStore(config)
    
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="test_user", session_id="test_session", tenant_id="local_dev")

    print("--- Scenario 1: Ambiguous Query ---")
    req1 = JetpackWizRequest(query="Compose UI")
    res1 = await inner_func(req1, context)
    print(f"\nAgent Reply (Is Interrupt? {res1.is_interrupt}):\n{res1.message}\n")
    
    if res1.is_interrupt:
        print("--- Scenario 2: Resolving Interrupt with '2' (compose/ui/ui) ---")
        req2 = JetpackWizRequest(query="2", user_reply="2")
        res2 = await inner_func(req2, context)
        print(f"\nAgent Final Reply:\n{res2.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
