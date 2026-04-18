# Pre-flight Plan: Upgrade Mock Queues

**Target Branch:** `track/upgrade-mock-queues-v4`

## Objective
Upgrade the mock infrastructure to support asynchronous background task processing using `asyncio.Queue` as specified in Codelab 3 requirements (`internal_ignore/inbox_gemini_cli/36_upgrade_mock_queues.md`).

## Proposed Changes
1. **mock_adapters.py**: Ensure the mock message broker (or renamed `MockMessageQueue`) natively uses `asyncio.Queue` for its publish/listen methods.
2. **chassis.py**: Update the `__init__` and `start()` methods to properly initialize this mock queue and ensure `@consume_task` background consumers are launched when `mock_infrastructure=True`.
3. **Tests**: Verify existing `test_consume_task` passes under the new implementation.