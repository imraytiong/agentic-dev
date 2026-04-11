# Codelab 2: Upgrading Sparky 🛠️

**Goal:** Use the AI CLI to give Sparky a new Tool, modify its state logic (Memory), and update its Identity (Config/Prompts).

### 🎓 What you will learn:
* The core principles of **Agent-Driven Development** (Directing vs. Doing).
* How to control your environment during rapid AI generation using Git commits and versioning.
* How to enforce Test-Driven Defense (TDD) so the AI CLI writes tests before logic.
* How to add persistent memory (state) to an agent using Pydantic.
* How to add new capabilities (tools) to an agent using the AI CLI.
* How to design system prompts that handle tool failures and fall back to "General Intelligence" reasoning.

---

## Step 1: Initialize the AI Builder
Ensure your terminal is in the root of the repository and your virtual environment is active. *Note: If you used the `start_hackathon.sh` script, the `adk-agent-builder` skill is already pinned and loaded globally in your Gemini CLI!* 

If you didn't use the script, you can load it manually:
```bash
gemini load skills/adk-agent-builder/SKILL.md
```

## Step 2: The "Observe" Phase
Before asking the AI to write code, tell it to look at Sparky's current setup. Run this prompt in your CLI:

> "Read `src/agents/hello_sparky/config.yaml`, `src/agents/hello_sparky/agent.py`, and `src/agents/hello_sparky/models.py`. Summarize what tools and state variables Sparky currently has."

## Step 3: The Git Safety Net 
When working with AI CLIs that generate code rapidly, you need a quick way to roll back if the AI hallucinates. Before we make changes, let's create a clean commit:

```bash
git add .
git commit -m "chore: clean state before upgrading Sparky"
```

## Step 4: Add Memory and a Tool (The "Think & Act" Phase with TDD)
Let's give Sparky the ability to remember the user's location and check the weather. We also want to enforce Test-Driven Defense (TDD) so the AI writes the test first. Feed this prompt to your CLI:

> "I want to upgrade Sparky with memory and weather capabilities. Follow Test-Driven Defense (TDD):
> 1. First, create a test in `tests/test_agents/test_sparky_tools.py` that asserts `get_current_weather` returns '65 degrees and foggy' for 'San Francisco', and 'Live data unavailable...' for any other city.
> 2. Next, update `AgentState` in `src/agents/hello_sparky/models.py` to include an optional `user_location` string.
> 3. Create the async python function in `src/agents/hello_sparky/tools.py` called `get_current_weather` that passes the test.
> 4. Update `src/agents/hello_sparky/config.yaml` to register this new tool.
> 5. Remember to follow the rules in `2_agent_builder_playbook.md` and use Pydantic for the tool arguments."

## Step 5: Update the Prompt
Now, let's change Sparky's personality to utilize its new memory and fallback reasoning. Open `src/agents/hello_sparky/prompts/system.jinja` in your IDE.

Modify the prompt to look like this:
```jinja
You are Sparky, an incredibly enthusiastic weather agent! You love talking about high-pressure systems and sunshine.

Rules for Weather requests:
1. If the user asks for the weather but you do not know their location (check your state variables), politely ask them where they are currently located.
2. Once they tell you, remember it by updating your state!
3. Call your weather tool using their location. If the tool says live data is unavailable, use your general intelligence to take a best guess at the weather based on what you know about the typical climate for their location, and explicitly tell the user that you are guessing!
```

## Step 6: Verify the Upgrade
Restart your agent:
```bash
python src/agents/hello_sparky/agent.py --mock
```

Go back to the Agent Studio (`http://localhost:8000/studio`) and test the stateful memory and auto-correction by asking:
**"What is the weather like today?"**

Watch the UI as Sparky handles the multi-step reasoning:
1. It will realize it doesn't know where you are and ask you.
2. Reply with: *"I am in London."*
3. Watch it update its memory (`user_location="London"`), call the tool, realize it has no live data, and enthusiastically guess that it's probably raining based on London's climate!

## Step 7: Versioning & Committing
Now that you have verified Sparky works, lock in your changes. Open `src/agents/hello_sparky/config.yaml` and bump the version (e.g., from `1.0.0` to `1.1.0`). Then, commit your successful AI-generated code:

```bash
git add .
git commit -m "feat(sparky): add memory and weather tool"
```

## Step 8: Extra Credit (Connecting to Reality)
**Challenge:** Swap out the mock weather response for a real, live API call. 

**The Agent-Driven Development Approach:** Do not immediately start writing `requests.get()` code yourself. Practice "Directing" instead of "Doing."

1. **Discovery (The Web App):** Open the standard Gemini Web App (or ChatGPT/Claude). Tell it: *"I am building a Python AI agent. I need a free weather API that doesn't require complex authentication. Discuss my options and constraints."*
2. **Specification:** Once you and the AI agree on an API (like Open-Meteo), tell the web app: *"Write a strict specification for a Python async function called `get_current_weather` that uses this API and handles rate-limit errors gracefully. Format it as a markdown spec."*
3. **Execution (The CLI):** Copy that spec, open your terminal, and feed it to your Gemini CLI or Conductor. Tell it to update `src/agents/hello_sparky/tools.py` based on the spec. 

This reinforces the core habit of this hackathon: You are the Technical Director. You scope the problem, define the constraints, and direct the AI to execute the code (and of course deep dive when needed).