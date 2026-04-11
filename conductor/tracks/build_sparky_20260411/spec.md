# Specification: Sparky Reference Agent

## Overview
Implement the "Hello Chassis" reference agent (Sparky) to verify the core platform functionality.

## Identity
- **Name:** `sparky` (as requested) / `hello_chassis` (as per spec)
- **Target Directory:** `src/agents/hello_sparky/`

## Requirements
- Consume from `hello_jobs` queue.
- Use `AgentContext` for all operations.
- Implement `HelloRequest`, `HelloState`, and `HelloResponse` models.
- Implement `get_affirmation` tool.
- Use Jinja2 system prompt.
- Verify via `pytest` and `chassis.run_local()`.
