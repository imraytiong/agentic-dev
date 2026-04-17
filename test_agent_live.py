import asyncio
import logging
import json
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from src.agents.jetpack_wiz.agent import register_jetpack_wiz_agent
from src.agents.jetpack_wiz.models import JetpackWizRequest
import yaml
import os

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    print("🚀 Starting LIVE test of the JetpackWiz Agent routing loop...\n")
    
    # 1. Setup Chassis
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=True)
    
    # 2. Register Agent
    agent_handler = register_jetpack_wiz_agent(chassis)
    
    # 3. Create a fake context
    context = AgentContext(user_id="test_user", session_id="test_session", tenant_id="local_dev")

    # 4. Scenario A: The Initial Request (Repo exists because of previous tests, so it should jump to Search)
    print("--- Scenario A: Discovery ---")
    req = JetpackWizRequest(query="Tell me about Compose UI")
    res = await agent_handler(req, context)
    print(f"Agent Reply:\n{res.message}\n")
    
    # 5. Scenario B: Disambiguation Interrupt
    print("--- Scenario B: Ambiguous Query ---")
    req2 = JetpackWizRequest(query="Compose")
    res2 = await agent_handler(req2, context)
    print(f"Agent Reply (Is Interrupt? {res2.is_interrupt}):\n{res2.message}\n")
    
    if res2.is_interrupt:
        # Simulate User picking option 1
        print("--- Scenario C: Resolving Interrupt with '1' ---")
        req3 = JetpackWizRequest(query="1", user_reply="1")
        res3 = await agent_handler(req3, context)
        print(f"Agent Reply:\n{res3.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
