# 🧠 AI Agent Engineering Dashboard

Welcome to your central command for AI Agent development. As your Technical Lead, I'll help you organize your architecture, track your daily progress, and map out agentic workflows.

## 🗂️ Workspace Organization

- **[src/agents/](../src/agents/)** - Active and planned AI agents.
  - 🐕 **[Sparky Spec](../src/agents/sparky_spec.md)** - "Sparky", our Hello World reference agent.

- **[developer_guides/](../developer_guides/)** - Developer guides for different roles:
  - 👑 **The Architect (Ray)**
    - 🚦 **[Architect Director Guide](../developer_guides/architecture_developers/architect_director_guide.md)** - How to direct CLIs to build the Universal Core.
  
  - ⚙️ **Infrastructure Leads (Platform Engineers)**
    - 🚦 **[Infrastructure Director Guide](../developer_guides/infrastructure_developers/infrastructure_director_guide.md)** - How to direct CLIs to build the platform spine.
    - 🧱 **[BaseAgentChassis Reference](../developer_guides/infrastructure_developers/baseagentchassis_reference.md)** - The Python skeleton for our distributed microservice chassis (Core + Adapters).
    - 🪄 **[BaseAgentChassis Internals](../developer_guides/infrastructure_developers/baseagentchassis_internals.md)** - The underlying magic of config merging and state management.

  - 🧑‍💻 **Agent Developers (App Engineers)**
    - 🚦 **[00 - Start Here](../developer_guides/agent_developers/00_start_here.md)** - Index and learning path for Agent Developers.
    - 🧠 **[Conceptual Guide](../developer_guides/agent_developers/conceptual_guide.md)** - High-level conceptual overview.
    - 📖 **[Developer Guide](../developer_guides/agent_developers/developer_guide.md)** - The definitive guide for writing agent code.
    - 🤖 **[Agentic Coding Playbook](../developer_guides/agent_developers/agentic_coding_playbook.md)** - How to direct AI coding agents.
    - 🎬 **[Agent Directing Guide](../developer_guides/agent_developers/agent_directing_guide.md)** - How to wield Gemini CLI + Conductor to build the codebase.
    - 🔄 **[Standard Agentic Workflows](../developer_guides/agent_developers/standard_agentic_workflows.md)** - Our approved patterns (Supervisor, Plan-and-Execute, Evaluator-Optimizer).

- **[spec_templates/](../spec_templates/)** - Standardized specification templates.
  - 📋 **[Agent Spec Template](../spec_templates/agent_spec_template.md)** - Use this when designing a new agent.
  - 📋 **[Adapter Spec Template](../spec_templates/adapter_spec_template.md)** - Use this when designing a new infrastructure adapter.

- **[src/universal_core/](../src/universal_core/)** - The sealed Universal Core.
  - 📋 **[Universal Core Architecture Spec](../src/universal_core/universal_core_architecture_spec.md)** - Use this to build the pristine base chassis logic.

- **[src/infrastructure/](../src/infrastructure/)** - The Hexagonal Adapters.
  - 📋 **[Fleet Infrastructure Spec](../src/infrastructure/fleet_infrastructure_spec.md)** - Use this to bootstrap the environment.

- **[internal_ignore/](./)** - Internal planning and unpolished scratchpads.
  - 🚀 **[Hackathon Execution Strategy](hackathon_execution_strategy.md)** - Division of labor and milestones for the upcoming hackathon.
  - 🏛️ **[Architectural Decision Log](architectural_decision_log.md)** - Master tracker for all technical decisions and open questions.

- **[skills/](../skills/)** - Exported skill files for your team to load into their AI CLIs.
  - 🤖 **[adk-agent-builder](../skills/adk-agent-builder/SKILL.md)**
  - 🤖 **[adk-infra-builder](../skills/adk-infra-builder/SKILL.md)**
  - 🤖 **[adk-core-builder](../skills/adk-core-builder/SKILL.md)**
  - 🤖 **[architecture-planning](../skills/architecture-planning/SKILL.md)**

## 🚀 Active Projects
- [Sparky Spec](../src/agents/sparky_spec.md)

---
*Tip: When you're ready to design an agent, let me know and we can draft an architecture spec together using our approved chassis.*