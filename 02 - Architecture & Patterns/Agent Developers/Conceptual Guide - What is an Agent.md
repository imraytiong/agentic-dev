---
links:
  - "[Developer Guide](Developer%20Guide.md)"
  - "[Agent Directing Guide](Agent%20Directing%20Guide.md)"
---
# Conceptual Guide: Building Agents in Our Ecosystem

**Tags:** #conceptual #onboarding #developer-guide
**Status:** Active Reference

Welcome! If you are a software engineer stepping into AI agent development for the first time, this guide is for you. 

Before we look at code, we need to shift how we think about building software. Here is a high-level, jargon-free breakdown of what an "Agent" is, what your job will be when building one, and what the underlying platform handles for you.

---

## 1. What is an "Agent"?

In traditional software, you write explicit `if/then` rules. If a user clicks a button, the code executes exactly steps 1, 2, and 3 in order. It is highly predictable, but it breaks if the user does something unexpected.

An **Agent** is simply a standard software service (like an API or a background worker) with a reasoning engine at its core. 

Instead of writing every `if/then` branch, you give the Agent:
1.  **A Goal:** "Find the error in this dataset."
2.  **Tools:** A set of standard functions it is allowed to use (e.g., `read_file`, `query_database`).
3.  **Rules:** "Do not delete any data. If you get stuck, ask for help."

The Agent reads the user's request, looks at its available tools, and autonomously decides which tools to run and in what order to achieve the goal. It is software that can plan, execute, evaluate its own work, and correct its own mistakes.

---

## 2. The Big Question: "Why not just use a prompt?"

If you've used Gemini, you might wonder why we need all this architecture. Why not just send a really good prompt to an AI model?

Here is the fundamental difference between a simple Prompt and an Agent:

*   **Action vs. Text:** A prompt generates text. It cannot *do* anything. An agent has "hands" (Tools). It can read a live database, parse a massive source repo, click a button, or send an email on your behalf.
*   **The Loop vs. The One-and-Done:** A prompt is a single transaction. You ask, it answers, and it stops. An agent operates in a continuous loop. If an agent tries to query a database and gets an error, it doesn't give up. It reads the error, realizes it made a typo, fixes the query, and tries again—autonomously.
*   **Context Management (The Memory Problem):** AI models have a limited "context window" (like a human's short-term working memory). You cannot paste a 10,000-page company manual into every single prompt. Agents solve this through **Context Management**. The platform stores massive amounts of data in long-term memory. When the agent faces a problem, it autonomously searches that memory, retrieves *only the three paragraphs relevant to the current task*, and injects them into its working memory. This allows the agent to be infinitely knowledgeable without overwhelming its brain.

---

## 3. Your Responsibilities (What You Build)

When you are tasked with building a new Agent, you are acting as the "Brain Architect" and the "Toolsmith." You will focus entirely on business logic. 

You will build four conceptual pieces:

### A. The Identity (Configuration)
You will create a simple configuration file. This tells the system the Agent's name, which AI model it should use (fast vs. smart), and which tools it is allowed to access. 

### B. The Brain (Instructions, Rules, and Skills)
You will write the Agent's core instructions in plain English text files. Think of this as writing an onboarding manual for a new human employee. You are taking a generalist AI model and turning it into a specialized expert by giving it:
*   **Persona & Specialized Knowledge:** "You are a senior financial analyst. Here is how we calculate Q3 revenue..." You are giving it the specific context it needs beyond its general training.
*   **Guardrails & Rules:** Strict boundaries on its behavior. "Never delete user data," "Always ask for human approval before sending an email," or "If you get stuck, stop and ask for help."
*   **Skills:** You can "equip" the agent with pre-packaged Skills. A Skill is a reusable bundle of specialized knowledge and tools you've already defined elsewhere. Instead of teaching every new agent how to analyze data from scratch, you just hand it the "Data Analyst Skill," and it instantly inherits that expertise and the rules that go with it.

### C. The Hands (Tools)
An AI cannot naturally interact with the outside world. If it needs to read a webpage, search a database, or send an email, you must write a standard software function to do that. You write the function, and the platform automatically translates it into a "button" the AI can press.

### D. The Controller (Business Logic & State)
You will write a single, clean file that acts as the traffic cop. This is where you define:
*   **State:** What variables does the Agent need to remember while working? (e.g., "I am on step 2 of 5").
*   **Dynamic Rules:** "If the user is a VIP, use the smartest AI model. Otherwise, use the fast one."
*   **Approval Loops:** "Let the AI draft the report, but don't send it until a human clicks approve."

---

## 4. The Hidden Magic (What the Platform Handles for You)

Building a distributed network of AI agents requires a massive amount of infrastructure. To let you focus purely on the logic above, our platform (the "Chassis") completely hides the plumbing. 

Here is what is happening on your behalf, automatically:

### A. Listening and Talking (Networking)
Your Agent needs to be able to receive requests from users and talk to other Agents. The platform automatically wraps your logic in a web server. When you want to ask another Agent a question, you just call a single command, and the platform handles finding that Agent on the network, sending the message securely, and waiting for the reply.

### B. Waiting in Line (Queues)
If a user asks your Agent to read a 500-page document, it might take 10 minutes. The platform automatically provides a background queue system. Your Agent can pick up massive jobs in the background, process them safely, and send a notification when it's done, without crashing or timing out.

### C. Remembering (Memory & Databases)
Agents need to remember things. The platform automatically connects your Agent to a centralized database. 
*   If your Agent needs to remember its current step in a workflow, the platform saves it automatically.
*   If your Agent needs to search through past conversations based on *meaning* (e.g., "Find the time we talked about security protocols"), the platform handles the complex math required to search concepts, not just keywords.

### D. Watching and Recording (Observability)
When an Agent makes a mistake, you need to know *why*. The platform automatically records every single thing the Agent does. It logs the exact prompt it was given, the tools it decided to use, the errors it hit, and how long it took. You get a visual dashboard of the Agent's entire "thought process" without writing a single line of logging code.

### E. Healing and Scaling (Infrastructure)
If your Agent gets confused and crashes, the platform detects the failure and instantly restarts it. If 1,000 users ask your Agent a question at the same time, the platform automatically clones your Agent to handle the traffic.

---

### Summary
Your job is to teach the Agent *how to think* and give it the *tools to act*. The platform ensures the Agent is secure, scalable, and always online.
## 5. The Multi-Agent System (MAS): Why not just one big Agent?

If Agents are so smart, why don't we just build one massive "God Agent," give it 50 tools, a 10-page instruction manual, and ask it to do everything?

Because it will fail. If you give a single AI too many instructions and too many tools, it gets confused. It forgets its persona, uses the wrong tools, hallucinates answers, and becomes incredibly slow and expensive to run.

Instead, we build a **Multi-Agent System (MAS)**—a "Society of Minds." We break complex problems down and assign them to a team of highly specialized, focused Agents that talk to each other. 

Here is how we use multiple Agents in our ecosystem:

### The "Factory Line" (Separation of Concerns)
Different tasks require different levels of intelligence. 
*   **Agent A (The Triage Agent)** uses a cheap, lightning-fast brain. It reads incoming customer emails, tags them, and drops them into a queue.
*   **Agent B (The Specialist)** uses a heavy, slower reasoning brain. It picks up the tagged email, searches the database, and drafts a highly technical response.
By splitting them up, the Specialist doesn't waste time reading spam, and the Triage agent stays incredibly fast.

### The "Debate" (Evaluator & Optimizer)
AI models are notoriously bad at catching their own mistakes on the first try. If an Agent writes code and reviews its own code in the same breath, it will often rubber-stamp its own errors.
*   **Agent A (The Drafter)** is instructed to be highly creative and write the code.
*   **Agent B (The Critic)** is instructed to be ruthless, detail-oriented, and focused strictly on finding flaws.
Agent A passes the code to Agent B. Agent B finds a flaw and sends it *back* to Agent A with a critique. This adversarial loop produces exponentially higher quality work than a single Agent trying to do both.

### The "Manager & Workers" (The Supervisor Pattern)
You want a single unified chat interface for your users, but you have vastly different capabilities in your backend.
*   **Agent A (The Front Door Manager)** is the only Agent the user talks to. Its only job is to figure out what the user wants and delegate the work.
*   **Agent B (The Deep Researcher)** specializes in reading massive PDFs.
*   **Agent C (The Data Analyst)** specializes in querying the database and drawing charts.
If a user asks a complex question, the Manager splits the task. It asks the Analyst for the numbers, asks the Researcher for the context, waits for both to reply, synthesizes the final answer, and hands it back to the user.

**The Chassis makes this easy:** Our platform handles all the underlying communication. If your Agent needs to ask another Agent a quick question, or drop a massive 10-minute job on another Agent's desk, it’s just one line of code.