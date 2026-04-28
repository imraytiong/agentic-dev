# ADK Learning Guide 

This document provides a quick reference and summary for all the codelabs available in the `learn/codelabs/` directory. These codelabs are designed to progressively teach you how to build, upgrade, and architect AI Agents using the Universal Core and Agent-Driven Development.

## [Codelab 1: Hello, Sparky! ⚡](codelabs/1_hello_sparky.md)
**Goal:** Get your environment running, boot up the agent framework (*Universal Core*), and interact with the reference agent (*Sparky*) via the built-in testing UI (*Agent Studio Web UI*).

**Key Learnings:**
* Bootstrapping the environment and running an agent in local "mock" mode.
* Interacting with agents via the Agent Studio UI and command-line REST API.
* Using the Gemini CLI to generate automated End-to-End tests.
* Exploring agent behavior, memory limitations, and persona boundaries.

## [Codelab 2: Upgrading Sparky 🛠️](codelabs/2_upgrading_sparky.md)
**Goal:** Use the AI CLI to give Sparky a new Tool, modify its state logic (Memory), and update its Identity (Config/Prompts).

**Key Learnings:**
* Core principles of **Agent-Driven Development** (Directing vs. Doing).
* Enforcing Test-Driven Defense (TDD) and Layer-by-Layer generation.
* Adding persistent memory (state) to an agent using Pydantic.
* Adding new capabilities (tools) like a weather checker.
* Designing system prompts that handle tool failures and fall back to "General Intelligence" reasoning.

## [Codelab 3: Developer API Intelligence Agent 🤖📱](codelabs/3_developer_api_intelligence_agent.md)
**Goal:** Build a sophisticated, real-world assistant that can analyze code repos (like AndroidX), track recent changes, and map developer shorthand names for repos to actual code modules.

**Key Learnings:**
* Handling long-running tasks (like cloning a repo) asynchronously using messaging queues to prevent UI freezing.
* Implementing State Management to track the progress of long-running tasks.
* Dynamic indexing and using Vector Databases for semantic search/translation (mapping shorthand to exact paths).
* Writing context-aware tools that execute real terminal commands (like `git log` and `git diff`) while protecting the LLM's context window.
* Mastering the **Observe, Think, Act, Verify** workflow for complex agent architectures.
