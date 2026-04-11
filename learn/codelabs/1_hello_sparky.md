# Codelab 1: Hello, Sparky! ⚡

**Goal:** Get your environment running, boot up the Universal Core, and interact with the reference agent (Sparky) via the Agent Studio Web UI.

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

## Step 4: The Agent Studio
Once the server boots, open your web browser and navigate to:
**[http://localhost:8000/studio](http://localhost:8000/studio)**

You are now in the Agent Studio! Try the following:
1. **Say Hello:** Type "Hello Sparky, what is your purpose?"
2. **Test Multimodal:** Click the paperclip icon, upload a small image or text file, and ask Sparky to describe it.

---
*Once you have successfully chatted with Sparky, you are ready for Codelab 2!*
