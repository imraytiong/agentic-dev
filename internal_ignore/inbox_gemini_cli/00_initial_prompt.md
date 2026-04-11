# Payload

Welcome to the project. Before you write any code, please do the following:
1. Read `README.md` to understand the directory structure.
2. Read `src/universal_core/universal_core_architecture_spec.md` as your primary source of truth for the codebase.
3. Note the existence of the `internal_ignore/inbox_scribe/` and `internal_ignore/inbox_gemini_cli/` directories. We will use these to pass complex context back and forth with Gemini Scribe. When creating a message, make a new file with a numeric prefix and short description (e.g., `00_my_message.md`).

**Do not generate any code yet.** Based on the spec and your loaded skill, map out the 5-layer execution plan for building the `BaseAgentChassis` and wait for my approval.