# Codelab 4: Capstone - Build Your Own Agent 🚀

Welcome to the final codelab! You've learned how to set up the environment, how to upgrade an existing agent, and you've seen the architectural roadmap required to build complex, long-running intelligence agents.

Now, it is time for the capstone challenge: **Building an agent from your own idea.**

This codelab will guide you through the entire lifecycle of Agent-Driven Development—from ideation to execution—drawing on everything you've learned.

### 🎓 What you will learn:
* How to use LLMs as brainstorming partners to scope and define a complex software problem.
* How to write a formal technical specification (`agent_spec_template.md`) that constrains AI code generation.
* How to execute the full "Observe -> Think -> Act -> Verify" loop to generate an entire agent layer-by-layer.
* How to integrate advanced concepts (queues, context management, graceful degradation) into a custom build.

---

## Step 1: Ideation & Discovery (The Sandbox)

Before you touch your CLI or write a single line of code, you need a solid idea. The best agents solve a specific, painful workflow problem.

**Your Task:**
1. Pick a workflow that annoys you or your team. (e.g., Triaging Jira tickets, summarizing weekly standup notes, writing boilerplate code reviews).
2. **Use an AI Assistant to Brainstorm:** Open the Gemini Web App (or your preferred conversational AI) on your second monitor. 
3. **The Discovery Prompt:** Tell the AI about your problem. E.g., *"I want to build an AI agent that helps me triage incoming GitHub issues. Ask me questions one by one to help me define the agent's persona, what external tools it will need, and what state it needs to remember."*
4. Keep it a discovery dialogue. Let the AI help you scope the problem down to something achievable in a hackathon.

## Step 2: The Specification (The Contract)

You are practicing "Directing" versus "Doing." You cannot just tell your CLI "Build my GitHub agent." It will hallucinate infrastructure and break the chassis rules. You must write a spec.

**Your Task:**
1. Copy the `spec_templates/agent_spec_template.md` file into your new agent's directory (e.g., `src/agents/my_custom_agent/my_agent_spec.md`).
2. Fill it out based on the brainstorming session you just completed.
3. **Crucial Details to Include:**
   * What is the exact data structure of the `AgentState`?
   * What specific tools does it need? (Remember from Codelab 2: how should it handle missing data?)
   * What is the exact system prompt/persona?

## Step 3: Execution (Directing the CLI)

Now you hand the contract to your builder.

**Your Task:**
1. Open your terminal and start your AI CLI (Gemini CLI or Conductor).
2. Load the agent builder skill: `gemini load skills/adk-agent-builder/SKILL.md`
3. Feed it your spec: *"Read `src/agents/my_custom_agent/my_agent_spec.md` and begin generating the code layer by layer according to your skill instructions."*
4. **Follow the Observe -> Think -> Act -> Verify loop.** Do not let the CLI generate the whole agent at once. Have it generate `models.py` first, then `tools.py`, then `agent.py`.

## Step 4: Advanced Capabilities (Leveling Up)

Draw on the concepts discussed in Codelab 3 to make your agent robust.

**Your Task (Consider the following):**
* **Long-Running Tasks:** Does your agent need to parse a lot of data? Make sure it's utilizing the async Redis queues (via `@chassis.consume_task`) so it doesn't block the UI.
* **Context Management:** If your agent pulls data from an API, how are you preventing it from blowing out the LLM's context window? (e.g., chunking text, summarizing before storing in state).
* **Graceful Degradation:** If an external API is down, does your agent crash, or does it politely inform the user and ask for alternative input?

## Step 5: Testing & Interaction

Once the CLI finishes generating the code, it's time to test your creation.

**Your Task:**
1. Run your agent in local mock mode: `python src/agents/my_custom_agent/agent.py --mock`
2. **Test via Agent Studio:** Open `http://localhost:8000/studio` and chat with your agent. Test out multimodal inputs—drop a relevant file into the chat and see if your agent processes it correctly.
3. **Test via MCP:** If you have an MCP-compatible IDE (like Cursor or Windsurf), connect it to `http://localhost:8000/mcp/sse` and try interacting with your agent directly from your codebase!

---
**Congratulations!** You have successfully completed the capstone codelab and built a production-ready agent using the BaseAgentChassis framework.