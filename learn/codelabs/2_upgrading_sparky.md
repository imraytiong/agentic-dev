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

If you didn't use the script, you can load it manually by copying and pasting this prompt into your CLI:

```text
please load adk-agent-builder
```
## Step 2: The "Observe" Phase
Before asking the AI to write code, tell it to look at Sparky's current setup. Instead of providing exact file paths, use a natural **Director Prompt**. Run this prompt in your CLI:

> "I am working on the Sparky agent. Please inspect its configuration, agent logic, and models, and summarize what tools and state variables Sparky currently has."

*(Notice how you didn't have to tell the AI to read `models.py` or `agent.py`? The `adk-agent-builder` skill already knows the architecture rules!)*

This allows you to inspect the current workings of Sparky. You can continue to ask the CLI questions about Sparky to get a good understanding of what Sparky is capable of doing. 

## Step 3: The Execution Prompt
Let's give Sparky the ability to remember the user's location and check the weather. We also want to enforce Test-Driven Defense (TDD) so the AI writes the test first.

Feed this exact prompt to your CLI:

> "I want to teach Sparky how to check the weather. Please update his state so he can remember the user's location. Then, build a tool that checks the weather (it can be a mock tool that reads from a simple configuration file since this is a codelab). If the tool can't find the location return that the weather for that location is not available. Please generate a plan."

> **Aside: The Art of Prompting**
> How you specify the prompt is entirely up to you. Even if you use a fluid, natural language prompt, it should be as detailed as possible so the initial plan generated is closer to your expectations. 
> 
> On the other hand, if you are not certain or don't have specific opinions about *how* a change should be implemented (like variable names or file structures), you can safely leave it up to the AI agent to determine that based on its loaded skill and the reference specifications it already has. 
> 
> *Warning:* If there isn't a specification or a loaded skill, the AI agent will take a best guess depending on the context and its general training, which will lead to less deterministic (and often hallucinated) code!
>
> **Example of a "Micro-Manager" Prompt:**
> If you *do* have strict opinions on the architecture, you can be highly technical: *"Update `AgentState` in `src/agents/hello_sparky/models.py` to include `Optional[str] user_location`. Then create `async def get_weather(location: str)` in `tools.py` returning a JSON string. If no data, return `{"error": "guess_climate"}`."*
> 
> **🌟 Extra Credit: The Vague Prompt Test**
> Before you approve the plan, try rejecting it! Tell the CLI: *"Actually, cancel that plan. Let's try this prompt instead: 'Let's make Sparky be able to tell the weather.'"* 
> 
> Observe what happens to the new plan. Notice how the AI fills in the blanks (often poorly, by over-engineering, or hallucinating files) when it isn't given strict boundaries or detailed instructions. Once you've seen the difference, ask it to revert back to the detailed plan!

## Step 4: Reviewing and Iterating on the Plan

Once the CLI prints out its **Layer-by-Layer Plan** (Models -> Tests -> Tools -> Brain -> Prompts), it will pause and wait for your approval. 

**Do not just blindly approve it!** You are the Technical Director. This pause is your opportunity to review the plan and iterate on it until you are satisfied. 

**Some things you can do while reviewing the plan:**
* **Refine the Logic:** If the AI's plan for the weather tool misses the fallback instruction (guessing based on climate data), tell it to fix the plan before proceeding.
* **Check the Layers:** Ensure it explicitly plans to write the test file (`test_sparky_tools.py`) *before* it writes the actual tool logic in Layer 3.
* **Ask Questions:** If you don't understand a Pydantic model or a library it proposes using, ask it to explain its reasoning.
* **Tweak the Architecture:** If you want the tool to be named something specific, or you want the state variable to be a list instead of a string, simply reply with your adjustments.

You can go back and forth with the CLI as many times as you need. Once the plan looks perfect, you can move to execution.

**Give planning revision a try:** run the prompt and observe how the AI agent proposes the architecture for your changes. Ask it to add 10 different weather scenarios for testing purposes to the plan if it didn't already suggest it. Or if it suggested it ask it to ensure that some places have adverse weather patterns.  

## Step 5: Directing the execution (The Loop)
Now you must act as the Director. Review the plan the CLI printed. If it looks correct, reply:

> "Approved. Execute Layer 1."

The CLI will modify `models.py` and pause again. You will repeat this loop:
* *"Execute Layer 2"* (Notice it writes `test_sparky_tools.py` *before* the tools!)
* *"Execute Layer 3"* (It writes the tool logic).
* *"Execute Layer 4"* (It updates the agent brain).
* **Important:** When you reach Layer 5 (Prompts), pause and look at Step 6 of this codelab before proceeding!

**Why do we pause at each layer?**
This layer-by-layer pause is crucial. It ensures the AI doesn't run off and hallucinate an entire codebase based on a faulty foundation. By pausing, you retain control as the Technical Director to verify each piece before the next one is built.

**What you should do during the pause:**
*   **Inspect the Code:** Open the actual `.py` files the CLI just generated and read them. Does the code match your expectations?
*   **Ask Questions:** If the CLI used a specific library or wrote a complex regex, ask it: *"Why did you use this library?"* or *"Can you explain how this logic works?"*
*   **Reject and Revise:** If the code is bad or misses the mark, you hold the power. You can reject the changes, drop the Git commit, and ask the CLI to rewrite the layer or make specific revisions before you approve moving forward.

**Aside: Incorporate Another Agent For Second Opinion:** 
You don't have to review the code alone! You can invite another human teammate (or even another AI agent) to peer-review the layer's implementation before proceeding to the next layer. 

> **Aside: The Git Safety Net**
> Because you are using the `adk-agent-builder` skill, the CLI will not just blindly generate code. It strictly enforces a **Git Safety Net** and a **Layered Approach**. When you gave it the prompt in Step 3, you probably noticed it automatically checked your `git status`, asked if you wanted to commit any pending work, and then created and checked out a **new feature branch** (e.g., `track/upgrade-sparky`). This protects you main branch and gives you a clean workspace!

## Step 6: The Stateful System Prompt (Layer 5)
When you tell the CLI to execute Layer 5 (Prompts), tell it to update the Jinja prompt to handle the new memory and tool fallback logic. 

Use a natural **Director Prompt** to explain the desired behavior:

> "For Layer 5, please update Sparky's system prompt to handle the new weather capabilities. Make sure Sparky knows to check its state for the user's location first. If it doesn't know the location, it should politely ask the user. Once it has the location, it should call the weather tool. Finally, ensure you add strict instructions that if the weather tool fails or returns no data, Sparky must use its general intelligence to guess the weather based on climate data, and explicitly tell the user it is guessing."

<details>
<summary><b>Example of a "Micro-Manager" Prompt</b></summary>

If you wanted to dictate the exact strings and rules (which is less flexible but more deterministic), it would look like this:

> "For Layer 5, update `src/agents/hello_sparky/prompts/system.jinja` with the exact following rules:
> 1. You are Sparky, an incredibly enthusiastic weather agent!
> 2. If the user asks for the weather but you do not know their location (check your state variables), politely ask them where they are.
> 3. Once they tell you, remember it by updating your state!
> 4. Call your weather tool. If the tool says live data is unavailable, use your general intelligence to take a best guess at the weather based on the typical climate for their location, and explicitly tell the user that you are guessing!"

</details>

## Step 7: Verify the Upgrade
Restart your agent:
```bash
source venv/bin/activate
python -m src.agents.hello_sparky.agent --mock
```

Go back to the Agent Studio (`http://localhost:8000/studio`) and test the stateful memory and auto-correction by asking:
**"What is the weather like today?"**

Watch the UI as Sparky handles the multi-step reasoning:
1. It will realize it doesn't know where you are and ask you.
2. Reply with: *"I am in London."*
3. Watch it update its memory (`user_location="London"`), call the tool, realize it has no live data, and enthusiastically guess that it's probably raining based on London's climate!

## Step 8: Versioning & Committing
Now that you have verified Sparky works, lock in your changes. Open `src/agents/hello_sparky/config.yaml` and bump the version (e.g., from `1.0.0` to `1.1.0`). Then, commit your successful AI-generated code:

```bash
git add .
git commit -m "feat(sparky): add memory and weather tool"
```

## Step 9: Extra Credit (Connecting to Reality)
**Challenge:** Swap out the mock weather response for a real, live API call. 

**The Agent-Driven Development Approach:** Do not immediately start writing `requests.get()` code yourself. Practice "Directing" instead of "Doing."

1. **Discovery (The Web App):** Open the standard Gemini Web App (or ChatGPT/Claude). Tell it: *"I am building a Python AI agent. I need a free weather API that doesn't require complex authentication. Discuss my options and constraints."*
2. **Specification:** Once you and the AI agree on an API (like Open-Meteo), tell the web app: *"Write a strict specification for a Python async function called `get_current_weather` that uses this API and handles rate-limit errors gracefully. Format it as a markdown spec."*
3. **Execution (The CLI):** Copy that spec, open your terminal, and feed it to your Gemini CLI or Conductor. Tell it to update `src/agents/hello_sparky/tools.py` based on the spec. 
4. **Fix annoying (unintentional) bugs:** There some obvious bugs with the solution.  Use the director development pattern to quickly patch them (hint Sparky seems to forget your name and doesn't know how to respond to some moods). 
	- Note how quickly you were able to patch the bug (versus hand debugging and fixing)
	- note sometimes it can get syntax incorrect :(.

This reinforces the core habit of this hackathon: You are the Technical Director. You scope the problem, define the constraints, and direct the AI to execute the code.

---

## 💡 Stuck? Need a Reference?
If you get completely stuck or want to compare your implementation against a "golden path" solution, you don't need to look in a separate folder. The reference solution is saved directly in this repository's Git history!

To view the completed code for this codelab, simply switch your branch in your terminal:
```bash
git checkout solution-codelab2
source venv/bin/activate
python -m src.agents.hello_sparky.agent --mock
```
*(You can easily switch back to your own work by running `git checkout main` or whichever branch you were working on!)*