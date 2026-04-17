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
    print("🚀 Starting LIVE test of the JetpackWiz Agent routing loop...\n")
    
    # 1. Setup Chassis
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=True)
    
    # 2. Register Agent
    register_jetpack_wiz_agent(chassis)
    
    # Get the raw underlying function by bypassing the @consume_task decorator
    inner_func = chassis._consumers[0].func
    
    # 3. Create a fake context
    context = AgentContext(user_id="test_user", session_id="test_session", tenant_id="local_dev")

    print("--- Scenario A: Status Ping ---")
    req_ping = JetpackWizRequest(query="how is it going?")
    res_ping = await inner_func(req_ping, context)
    print(f"Agent Reply:\n{res_ping.message}\n")

    print("--- Scenario B: Ambiguous Query ---")
    # Because we restarted the script, the mock vector store is empty.
    # The agent will detect this (state.has_indexed = False) and trigger ensuring the repo.
    req2 = JetpackWizRequest(query="Compose")
    res2 = await inner_func(req2, context)
    print(f"Agent Reply (Is Interrupt? {res2.is_interrupt}):\n{res2.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
