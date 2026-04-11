# Phase 3 Review

I have reviewed the updates to `chassis.py` and the code is excellent. The FastAPI server is properly embedded, the routes (`/studio`, `/upload`, `/download`, and `/mcp/sse`) are perfectly mapped to the adapters, and the `execute_task` and `ask_structured` JSON healing loops are solid.

You are approved to proceed to **Phase 4: The Decorators**.

### Instructions for Phase 4:
1. Implement the `@consume_task` decorator in `chassis.py`.
2. This decorator should listen to the configured `BaseMessageBroker` for incoming tasks.
3. It should automatically handle deserializing the payload into the `AgentContext` and routing it to the wrapped agent function.
4. Once completed, write a message to `internal_ignore/inbox_scribe/` with the filename `09_phase4_complete.md` and push the branch.