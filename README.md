# AI Agent Engineering Framework

## Overview
This repository is a framework and playbook for building distributed AI agents using the Google Agent Development Kit (ADK) and Python. 

It is designed for **Agent-Driven Development**. If you are comfortable with Git, the command line, and prompt engineering (using tools like Gemini CLI or Antigravity) but have zero familiarity with developing AI agents, this repo will kick-start that process. We provide the architectural guardrails, playbooks, and AI instructions needed to safely direct your AI assistants to write the code for you.

## ⚠️ Prerequisites
Before running the quick start script, you **must** have the following installed on your machine:
1. **Python 3** (and `venv` module)
2. **Gemini CLI** (e.g., `npm install -g @google/generative-ai-cli` or your internal equivalent)

## Quick Start
To instantly set up your local environment, clone the repo, and initialize your AI CLI with the correct guardrails, run this single command in your terminal:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/imraytiong/agentic-dev/main/scripts/start_hackathon.sh)"
```

> **Note for Corporate Environments:** If your environment uses an alias for the Gemini CLI (e.g., `ai` instead of `gemini`), the script may exit before launching the CLI. If that happens, simply navigate into the newly created directory and run your aliased command (e.g., `ai`) to start.

**Next Steps:**
The setup script will automatically drop you directly into the Gemini CLI. The `adk-agent-builder` skill is already pinned and loaded for you globally, so you can immediately start directing your AI to build!

## System Architecture

The codebase relies on a Hexagonal (Ports & Adapters) architecture that allows us to maintain an open-source core while building proprietary logic safely on top of it.

```mermaid
flowchart TD
    %% Styling
    classDef core fill:#2b3a42,stroke:#3f5765,stroke-width:2px,color:#fff;
    classDef public fill:#1e4620,stroke:#2e6b32,stroke-width:2px,color:#fff;
    classDef private fill:#5c1e1e,stroke:#8a2e2e,stroke-width:2px,color:#fff;
    classDef cfgNode fill:#4a4a4a,stroke:#666666,stroke-width:2px,color:#fff;

    %% Nodes
    FleetConfig["Fleet Config (fleet.yaml)<br/>Base Dependencies"]:::cfgNode

    subgraph CoreLayer [Universal Core]
        Chassis(BaseAgentChassis):::core
        Interfaces(Abstract Interfaces / Ports):::core
        Chassis --> Interfaces
    end

    subgraph AgentLayer [Agent Microservices]
        AgentConfig["Agent Config (config.yaml)<br/>Agent Specifics"]:::cfgNode
        CustomAgents["Custom Agents 🌐/🔒"]:::public
        AgentConfig -. Configures .-> CustomAgents
    end

    subgraph InfraLayer [Infrastructure Adapters]
        MsgQueue["Message Queue Adapters 🌐<br/>Redis, Kafka"]:::public
        DBAdapter["Database Adapters 🌐<br/>Postgres, pgvector"]:::public
        CustomAPI["Custom API Adapters 🔒<br/>Internal Services"]:::private
    end

    %% Connections
    FleetConfig -. Injects dependencies .-> Chassis
    CustomAgents -- Inherits --> Chassis

    Interfaces -. Implemented by .-> MsgQueue
    Interfaces -. Implemented by .-> DBAdapter
    Interfaces -. Implemented by .-> CustomAPI
```
*(Legend: 🌐 = Open Source / Public Repository, 🔒 = Corporate Internal Repository)*

## Directory Structure

*   **[src/agents/](src/agents/)** — Active or reference agent implementations. Code for agents goes here.
*   **[src/infrastructure/](src/infrastructure/)** — Where the Hexagonal Adapters live (e.g., standard Redis, Postgres) and the `fleet_infrastructure_spec.md`. Code for infrastructure goes here.
*   **[src/universal_core/](src/universal_core/)** — The sealed Universal Core (`BaseAgentChassis`), system contracts, boundaries, and the `universal_core_architecture_spec.md`.
*   **[developer_guides/](developer_guides/)** — The core playbooks and instructions. This is where human developers learn how to build and direct agents.
*   **[spec_templates/](spec_templates/)** — Templates for technical specifications (e.g., agents, adapters).
*   **[skills/](skills/)** — Pre-packaged AI CLI instructions (`SKILL.md` files). Load these into your AI coding assistant to enforce our architectural rules during code generation.
*   **[internal_ignore/](internal_ignore/)** — **Safe to ignore.** For the curious: this contains internal workspace files, architectural decision logs, and hackathon planning scratchpads for the core maintainers. 

## Where to Start

Depending on what you want to build, choose your role and follow the entry point:

### 1. Agent Developers
*Your focus: Writing business logic, tools, and prompts. You do not need to worry about infrastructure.*
*   [Concepts](developer_guides/agent_developers/1_agent_concepts.md)
*   [Start Building](developer_guides/agent_developers/2_agent_builder_playbook.md)
*   [Code Reference](developer_guides/agent_developers/3_code_reference.md)
*   [Deep Topics (Homework)](developer_guides/agent_developers/4_agent_deep_topics.md)

### 2. Infrastructure Developers
*Your focus: Deployments, containers, adapters, and mapping the environment (Docker/K3s).*
*   [Concepts](developer_guides/infrastructure_developers/1_infrastructure_concepts.md)
*   [Start Building](developer_guides/infrastructure_developers/2_infrastructure_playbook.md)
*   [Code Reference](developer_guides/infrastructure_developers/3_core_internals_reference.md)
*   [Deep Topics (Homework)](developer_guides/infrastructure_developers/4_infrastructure_deep_topics.md)

### 3. Architecture Developers
*Your focus: Maintaining the sealed Universal Core (`BaseAgentChassis`), system contracts, and boundaries.*
*   [Concepts](developer_guides/architecture_developers/1_architecture_concepts.md)
*   [Start Building](developer_guides/architecture_developers/2_architecture_playbook.md)
*   [Code Reference](developer_guides/architecture_developers/3_architecture_reference.md)
*   [Deep Topics (Homework)](developer_guides/architecture_developers/4_architecture_deep_topics.md)

### Codelabs
We have prepared a set of Codelabs to get you up to speed quickly:
* [Codelab 1: Hello Sparky!](learn/codelabs/1_hello_sparky.md) - Environment setup and running your first agent.
* [Codelab 2: Upgrading Sparky](learn/codelabs/2_upgrading_sparky.md) - Adding tools and modifying agent behavior using the AI CLI.
* [Codelab 3: Developer API Intelligence Agent](learn/codelabs/3_developer_api_intelligence_agent.md) - Advanced challenge to build a real-world code repo assistant.
* [Codelab 4: Capstone - Build Your Own Agent](learn/codelabs/4_capstone_build_your_own.md) - Take a rough idea, create a spec, and direct the CLI to build your custom agent