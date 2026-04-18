# Pre-flight Plan: Upgrade Mock Queues

**Target Branch:** `track/upgrade-mock-queues-final`

## Objective
Execute the mock queue upgrade requested in `internal_ignore/inbox_gemini_cli/36_upgrade_mock_queues.md`.

## Proposed Changes
1. Analyze `src/universal_core/chassis.py` and `mock_adapters.py` to identify the current implementation of the mock message queue.
2. Ensure the mock queue natively uses `asyncio.Queue` to enqueue and dequeue tasks in memory.
3. Verify that the `start()` method in `chassis.py` boots the background consumers (tasks registered via `@consume_task`) when `mock_infrastructure=True`.
4. Run tests to confirm the mock background worker behaves asynchronously.