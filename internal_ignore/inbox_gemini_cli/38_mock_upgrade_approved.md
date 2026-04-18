# Approval: Mock Queue Upgrade Plan

The pre-flight plan in `00_upgrade_mock_queues_plan_final.md` looks perfect. 

Please proceed with executing the plan on the `track/upgrade-mock-queues-final` branch. 

Modify `chassis.py` (and any related mock adapter files) to upgrade the mock queue to use `asyncio.Queue` and ensure background consumers boot correctly when `mock_infrastructure=True`. 

Once finished, commit your changes, push the branch, and drop a completion message in the Scribe inbox.