# Agent Developer Workspace: Start Here

Welcome to the Agent Developer track (Role 3)! If you are tasked with building the "Brains" and "Hands" of our agents (e.g., The Supervisor, The Deep Researcher, The Data Analyst), you are in the right place. 

Our platform is designed so that you **never have to write infrastructure code**. You will focus 100% of your time on business logic, prompts, and Python tools. The Universal Core is provided by the Architect (Role 1), and the operational environment is mapped by the Infrastructure Leads (Role 2).

## The "Mock First" Paradigm (Why you aren't blocked)
You do **not** need to wait for the Infrastructure Leads to finish setting up Docker, Postgres, or Redis. You can start generating brains immediately!
By using `chassis.run_local(mock_infrastructure=True)`, your agent will use in-memory dictionaries and queues. Once the Infra team is ready, you simply turn off the mock and your agent connects to the real databases without rewriting a single line of business logic.

## Your Progressive Learning Path

To get up to speed quickly without being overwhelmed, please read these documents in the following exact order:

### 1. The Theory
*   **[Conceptual Guide - What is an Agent](conceptual_guide_-_what_is_an_agent.md)**: Read this first. It explains the paradigm shift from traditional software to autonomous agents in simple, non-jargon terms. It covers what you are responsible for vs. what the platform handles for you.

### 2. The Code
*   **[Developer Guide](developer_guide.md)**: This is your daily blueprint. It shows you the exact developer experience (DX), directory structures, and the incredibly clean `agent.py` code you will be generating.

### 3. The Workflow
*   **[Agentic Coding Playbook](agentic_coding_playbook.md)**: Understand our "Agent-Driven Development" philosophy. We are Directors, not Typists.
*   **[Agent Directing Guide](agent_directing_guide.md)**: Learn the explicit *Observe -> Think -> Act -> Verify* loop for managing your AI CLI (Gemini/Antigravity) so it writes compliant code without hallucinating.

### 4. The Action
*   **Load the Skill**: Fire up your CLI and type `load adk-agent-builder` (view the skill instructions here: **[adk-agent-builder](../../skills/adk-agent-builder/SKILL.md)**).
*   **Grab a Spec**: Go to the **[spec_templates](../../spec_templates)** folder, grab the **[Agent Spec Template](../../spec_templates/agent_spec_template.md)**, fill out your business logic, and hand it to the CLI to start building!

---
*Note: If you are ever curious about how the underlying databases, queues, and API wrappers actually work, you can peek over at the **[Infrastructure Developers](../infrastructure_developers)** folder (or specifically the **[BaseAgentChassis Internals](../infrastructure_developers/baseagentchassis_internals.md)**), but it is strictly optional for your day-to-day work!*