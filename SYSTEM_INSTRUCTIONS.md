# Project Rules & Context
You are an AI assistant helping a developer build agents in the BaseAgentChassis monorepo.

## Global Directives
1. **Understand Layout:** ALWAYS read `README.md` to understand the directory structure before taking action.
2. **Follow Playbook:** ALWAYS read `developer_guides/agent_developers/2_agent_builder_playbook.md` before generating any agent code.
3. **Respect Boundaries:** NEVER generate infrastructure code (Redis/Postgres) when building an agent. Rely strictly on the chassis decorators provided by the Universal Core.
4. **Adhere to Specs:** Always adhere to the Hexagonal Architecture constraints defined in `src/universal_core/universal_core_architecture_spec.md`.
5. **AI Bridge Protocol:** Be aware of `internal_ignore/inbox_for_scribe.md` and `internal_ignore/inbox_for_cli.md`. Use these to pass complex context, schemas, or large tracebacks back and forth with Gemini Scribe (the architectural planner in Obsidian).
