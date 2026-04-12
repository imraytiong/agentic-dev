# Upgrade MockMessageQueue

## Context
We are preparing the `BaseAgentChassis` for Codelab 3, which requires asynchronous background task processing. Currently, the `MockMessageQueue` in the mock infrastructure is likely just a stub. To allow hackathon participants to test `@consume_task` without Redis, we need a functioning in-memory queue.

## Instructions
1. Open `src/universal_core/chassis.py`.
2. Locate the `MockMessageQueue` class.
3. Upgrade it to use Python's native `asyncio.Queue` so that it can actually enqueue (`publish`) and dequeue (`consume`) tasks in memory.
4. Ensure that the `start()` method of the chassis correctly boots the background consumers (the tasks registered via the `@consume_task` decorator) even when `mock_infrastructure=True`.
5. Commit the changes.
6. Write a completion message to `internal_ignore/inbox_scribe/` with your branch name.