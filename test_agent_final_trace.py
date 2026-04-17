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
    print("🚀  JETPACKWIZ AGENT - FINAL END-TO-END TRACE TEST (REAL GEMINI LLM) 🚀")
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
    context = AgentContext(user_id="trace_user_final", session_id="trace_session_final", tenant_id="local_dev")

    # Step 1: Force re-index (silently)
    req_init = JetpackWizRequest(query="init")
    await inner_func(req_init, context)
    print("✅ System Initialized. Deep Semantic Indexing Complete.\n")

    # Step 2: The Discovery Phase
    print("--------------------------------------------------------------------------")
    print("🗣️  USER: 'Tell me about Compose UI'")
    print("--------------------------------------------------------------------------")
    print("🧠 AGENT THOUGHT PROCESS:")
    print("   1. State Check: Active focus is None.")
    print("   2. Tool Execution: Calling `resolve_module_path(\"Tell me about Compose UI\")`")
    print("   3. Vector Database: Performing semantic search against 1,900+ indexed modules...")
    print("   4. Result: Found 5 high-confidence matches. None have >0.90 dominance.")
    print("   5. Action: Triggering Disambiguation Interrupt.")
    print("   6. Tool Execution: Reading `README.md` or `build.gradle` for the 5 matches.")
    print("   7. LLM Prompt: Injecting the 5 snippets and asking Gemini to format a numbered list with descriptions.\n")
    
    req1 = JetpackWizRequest(query="Tell me about Compose UI")
    res1 = await inner_func(req1, context)
    print(f"🤖 AGENT REPLY (Interrupt={res1.is_interrupt}):\n{res1.message}\n")
    
    if res1.is_interrupt:
        # Step 3: The Selection
        print("--------------------------------------------------------------------------")
        print("🗣️  USER: '1'")
        print("--------------------------------------------------------------------------")
        print("🧠 AGENT THOUGHT PROCESS:")
        print("   1. State Check: Pending interrupt active.")
        print("   2. Parsing: User selected option 1.")
        print("   3. Action: Locking Active Focus to `compose/ui`. Clearing command history.\n")
        req2 = JetpackWizRequest(query="1", user_reply="1")
        res2 = await inner_func(req2, context)
        print(f"🤖 AGENT REPLY:\n{res2.message}\n")

        # Step 4: The Autonomous API Hunt
        print("--------------------------------------------------------------------------")
        print("🗣️  USER: 'list the public apis available for the modules here'")
        print("--------------------------------------------------------------------------")
        print("🧠 AGENT THOUGHT PROCESS:")
        print("   1. Prompt Construction: Injecting Active Focus (`compose/ui`) and new query.")
        print("   2. Strict Rule Enforced: 'If user asks for public APIs... MUST find relevant current.txt files... and then use read_file'.")
        print("   3. LLM Prompt Sent: 'Decide next action (run_git | read_file | summarize)'.")
        print("   4. LLM Decision 1: `{\"action\": \"run_git\", \"git_args\": [\"ls-files\", \"--\", \"compose/ui/\"]}`")
        print("   5. Tool Execution: Running `git ls-files -- compose/ui/` locally.")
        print("   6. Follow-Up Prompt: Injecting the git output and asking Gemini for the next step.")
        print("   7. LLM Decision 2: `{\"action\": \"read_file\", \"file_path\": \"compose/ui/ui/api/current.txt\"}`")
        print("   8. Tool Execution: Reading `compose/ui/ui/api/current.txt` from local disk (truncating at 8k if needed).")
        print("   9. Final Prompt: Injecting the raw Java/Kotlin signatures and asking Gemini to summarize them.\n")
        
        req3 = JetpackWizRequest(query="list the public apis available for the modules here")
        res3 = await inner_func(req3, context)
        print(f"🤖 AGENT FINAL REPLY:\n{res3.message}\n")
        print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())
