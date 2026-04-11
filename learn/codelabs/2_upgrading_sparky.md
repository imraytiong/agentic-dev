# Codelab 2: Upgrading Sparky 🛠️

**Goal:** Use the AI CLI to give Sparky a new Tool, modify its state logic (Memory), and update its Identity (Config/Prompts).

## Step 1: Initialize the AI Builder
Ensure your terminal is in the root of the repository and your virtual environment is active. Load the Agent Builder skill into your AI CLI:

```bash
gemini load skills/adk-agent-builder/SKILL.md
```

## Step 2: The "Observe" Phase
Before asking the AI to write code, tell it to look at Sparky's current setup. Run this prompt in your CLI:

> "Read `src/agents/hello_sparky/config.yaml`, `src/agents/hello_sparky/agent.py`, and `src/agents/hello_sparky/models.py`. Summarize what tools and state variables Sparky currently has."

## Step 3: Add Memory and a Tool (The "Think & Act" Phase)
Let's give Sparky the ability to remember the user's location and check the weather. Feed this prompt to your CLI:

> "I want to upgrade Sparky with memory and weather capabilities.
> 1. Update `AgentState` in `src/agents/hello_sparky/models.py` to include an optional `user_location` string.
> 2. Create an async python function in `src/agents/hello_sparky/tools.py` called `get_current_weather`. It should require a `location` string. If the location is 'San Francisco', return '65 degrees and foggy'. For any other location, return a string saying: 'Live data unavailable for [location]. Fallback to general climate knowledge.'
> 3. Update `src/agents/hello_sparky/config.yaml` to register this new tool.
> 4. Remember to follow the rules in `2_agent_builder_playbook.md` and use Pydantic for the tool arguments."

## Step 4: Update the Prompt
Now, let's change Sparky's personality to utilize its new memory and fallback reasoning. Open `src/agents/hello_sparky/prompts/system.jinja` in your IDE.

Modify the prompt to look like this:
```jinja
You are Sparky, an incredibly enthusiastic weather agent! You love talking about high-pressure systems and sunshine.

Rules for Weather requests:
1. If the user asks for the weather but you do not know their location (check your state variables), politely ask them where they are currently located.
2. Once they tell you, remember it by updating your state!
3. Call your weather tool using their location. If the tool says live data is unavailable, use your general intelligence to take a best guess at the weather based on what you know about the typical climate for their location, and explicitly tell the user that you are guessing!
```

## Step 5: Verify the Upgrade
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

## Step 6: Extra Credit (Connecting to Reality)
**Challenge:** Swap out the mock weather response for a real, live API call. 

**The Agent-Driven Development Approach:** Do not immediately start writing `requests.get()` code yourself. Practice "Directing" instead of "Doing."

1. **Discovery (The Web App):** Open the standard Gemini Web App (or ChatGPT/Claude). Tell it: *"I am building a Python AI agent. I need a free weather API that doesn't require complex authentication. Discuss my options and constraints."*
2. **Specification:** Once you and the AI agree on an API (like Open-Meteo), tell the web app: *"Write a strict specification for a Python async function called `get_current_weather` that uses this API and handles rate-limit errors gracefully. Format it as a markdown spec."*
3. **Execution (The CLI):** Copy that spec, open your terminal, and feed it to your Gemini CLI or Conductor. Tell it to update `src/agents/hello_sparky/tools.py` based on the spec. 

This reinforces the core habit of this hackathon: You are the Technical Director. You scope the problem, define the constraints, and direct the AI to execute the code (and of course deep dive when needed).