import asyncio
import logging
import json
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from src.agents.jetpack_wiz.agent import register_jetpack_wiz_agent
from src.agents.jetpack_wiz.models import JetpackWizRequest
import yaml

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    print("🚀 Starting LIVE test of the JetpackWiz Agent routing loop (with LLM)...\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=True)
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="test_user", session_id="test_session", tenant_id="local_dev")

    # We skip re-indexing by pretending it's already done to speed this up, 
    # but we must populate the vector store with at least one mock result for the interrupt to work.
    mock_vector_store = chassis.vector_store
    
    # We will simulate the user asking for "Compose UI" which triggers an interrupt
    print("--- Scenario 1: Ambiguous Query ---")
    req1 = JetpackWizRequest(query="Compose UI")
    res1 = await inner_func(req1, context)
    print(f"Agent Reply (Is Interrupt? {res1.is_interrupt}):\n{res1.message}\n")
    
    if res1.is_interrupt:
        # Simulate User picking option 3 ("compose/ui")
        print("--- Scenario 2: Resolving Interrupt with '3' ---")
        req2 = JetpackWizRequest(query="3", user_reply="3")
        res2 = await inner_func(req2, context)
        print(f"Agent Final Reply:\n{res2.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
