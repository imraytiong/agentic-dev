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
    print("🚀 Starting TRACE test of JetpackWiz (REAL GEMINI LLM)...\n")
    
    config_path = "src/agents/jetpack_wiz/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    chassis = BaseAgentChassis(config, mock_infrastructure=False)
    
    from src.universal_core.mock_adapters import MockVectorStore, MockStateStore
    chassis.vector_store = MockVectorStore()
    chassis.state_store = MockStateStore(config)
    
    register_jetpack_wiz_agent(chassis)
    inner_func = chassis._consumers[0].func
    context = AgentContext(user_id="trace_user", session_id="trace_session", tenant_id="local_dev")

    # Step 1: Force re-index (silently) so we have a populated vector store
    req_init = JetpackWizRequest(query="init")
    await inner_func(req_init, context)

    # Step 2: Trigger the search and disambiguation
    print("==================================================")
    print("🗣️  USER: Tell me about Compose UI")
    print("==================================================")
    req1 = JetpackWizRequest(query="Tell me about Compose UI")
    res1 = await inner_func(req1, context)
    print(f"🤖 AGENT: {res1.message}\n")
    
    if res1.is_interrupt:
        # Step 3: Resolve interrupt
        print("==================================================")
        print("🗣️  USER: 1")
        print("==================================================")
        req2 = JetpackWizRequest(query="1", user_reply="1")
        res2 = await inner_func(req2, context)
        print(f"🤖 AGENT: {res2.message}\n")

        # Step 4: Ask it to read a specific current.txt file
        print("==================================================")
        print("🗣️  USER: Read the api/current.txt for the ui-geometry submodule and list its public APIs.")
        print("==================================================")
        req3 = JetpackWizRequest(query="Read the api/current.txt for the ui-geometry submodule and list its public APIs.")
        res3 = await inner_func(req3, context)
        print(f"🤖 AGENT: {res3.message}\n")

if __name__ == "__main__":
    asyncio.run(main())
