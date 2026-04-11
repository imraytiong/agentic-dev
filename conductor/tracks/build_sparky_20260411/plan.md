# Implementation Plan: Sparky Reference Agent

## Layer 1: Data
- [ ] Task: Generate `src/agents/hello_sparky/models.py` (Request, State, Response schemas)

## Layer 2: Defense (Testing)
- [ ] Task: Generate `src/agents/hello_sparky/tests/test_tools.py`
- [ ] Task: Generate `src/agents/hello_sparky/tests/test_agent.py`

## Layer 3: Capabilities (Tools)
- [ ] Task: Generate `src/agents/hello_sparky/tools.py` (get_affirmation function)

## Layer 4: The Brain (Agent)
- [ ] Task: Generate `src/agents/hello_sparky/agent.py` using `BaseAgentChassis`

## Layer 5: Configuration & Prompts
- [ ] Task: Generate `src/agents/hello_sparky/config.yaml`
- [ ] Task: Generate `src/agents/hello_sparky/prompts/system_prompt.jinja`

## Final Validation
- [ ] Task: Run `pytest` and verify local execution with mock infrastructure.
