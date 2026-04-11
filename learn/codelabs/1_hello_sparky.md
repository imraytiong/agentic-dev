# Codelab 1: Hello, Sparky! ⚡

**Goal:** Get your environment running, boot up the Universal Core, and interact with the reference agent (Sparky) via the Agent Studio Web UI.

### 🎓 What you will learn:
* How to bootstrap the monorepo environment and AI context.
* How to run the `BaseAgentChassis` in local "mock" mode.
* How to interact with your agents natively via the Agent Studio Web UI.
* How to test multimodal inputs (file uploads) with your agent.
* How to manually inspect an agent's reasoning loop by interacting with it and observing its behavior.

---

## Step 1: The One-Click Setup
We have automated the entire environment setup. Open your terminal, navigate to the root of the repository, and run the bootstrap script:

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```
*What this does: Copies your `.env`, builds your Python virtual environment, installs the dependencies, and initializes your AI CLI with the correct context.*

## Step 2: Activate the Environment
Always ensure your virtual environment is active before running the code:
```bash
source venv/bin/activate
```

## Step 3: Boot Sparky
We are going to run Sparky using the `mock_infrastructure` flag. This bypasses the need for enterprise Redis/Postgres and spins everything up locally in memory.

```bash
python src/agents/hello_sparky/agent.py --mock
```

## Step 4: The Agent Studio & Manual Inspection
Once the server boots, open your web browser and navigate to:
**[http://localhost:8000/studio](http://localhost:8000/studio)**

You are now in the Agent Studio! Try the following to manually inspect the agent:
1. **Say Hello:** Type "Hello Sparky, what is your purpose?" Watch how the agent responds.
2. **Test Multimodal:** Click the paperclip icon, upload a small image or text file, and ask Sparky to describe it.
3. **Observe the Loop:** As Sparky processes your inputs, pay attention to any status updates, tool calls, or intermediate reasoning steps that the UI (or your terminal console) displays. This manual inspection is critical for understanding *how* the agent arrives at its answers.

---
*Once you have successfully chatted with Sparky, you are ready for Codelab 2!*
