# Codelab 1: Hello, Sparky! ⚡

**Goal:** Get your environment running, boot up the agent framework (*Universal Core*), and interact with the reference agent (*Sparky*) via the built in testing UI (*Agent Studio Web U*I).

### 🎓 What you will learn:
* How to bootstrap the environment
* How to run an agent in local "mock" mode
* How to interact with your agents natively via the built in  testing UI 

---

## Step 1: The One-Click Setup
We have automated the entire environment setup. Open your terminal and run the bootstrap script:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/imraytiong/agentic-dev/main/scripts/start_hackathon.sh)"
```
*What this does: Clones the repo, copies your `.env`, builds your Python virtual environment, installs the dependencies, initializes your AI CLI with the correct context, and drops you directly into the Gemini CLI.*

## Step 2: Exit the CLI (For Now)
Since we want to manually run the Sparky agent first, type `exit` in the Gemini CLI. You will still be inside the `agentic-dev` directory with your Python virtual environment activated!

- Control + C twice will exit the CLI. 
## Step 3: Boot Sparky
We are going to run Sparky using the `mock_infrastructure` flag. This bypasses the need for enterprise Redis/Postgres and spins everything up locally in memory.

```bash
python -m src.agents.hello_sparky.agent --mock
```

## Step 4: Manual Inspection
Once the server boots, open your web browser and navigate to:
**[http://localhost:8000/studio](http://localhost:8000/studio)**

- *If you're running remotely on a virtual desktop or container you might be able to connect via it's URI from your local machine. This is dependent on your private network policies and remote machine restrictions. Otherwise you will likely need to login via screen sharing* 

You are now in the Agent Studio, a built in basic UI that will allow you to interact with your agent. Try the following to manually inspect the agent:
1. **Say Hello:** Type "Hello Sparky, what is your purpose?" Watch how the agent responds.
2. **Test Multimodal (The Limitation):** Click the paperclip icon, upload a small image or text file, and ask Sparky to describe it. *Notice how Sparky ignores the file or gets confused!* This is because while the UI supports file uploads, Sparky's current `HelloRequest` schema and prompt are strictly built for text. You will learn how to expand agent schemas to fix limitations like this later!
3. **Observe the Loop:** As Sparky processes your inputs, pay attention to any status updates, tool calls, or intermediate reasoning steps that the UI (or your terminal console) displays. This manual inspection is critical for understanding *how* the agent arrives at its answers.

---
*Once you have successfully chatted with Sparky, you are ready for Codelab 2!*

## Step 5: Extra Credit (For the Fast Finishers)
If you finished early and are waiting for others to catch up, try this:
1. **Break the UI:** Open `http://localhost:8000/studio`, open your browser's Developer Tools (Network tab), and watch the `/chat` endpoint fire when you send a message. What does the JSON payload look like?
2. **Break the CLI:** Try asking Sparky something completely outside its persona (e.g., "Write me a Python script"). See how the LLM handles it based on its current bare-bones prompt.