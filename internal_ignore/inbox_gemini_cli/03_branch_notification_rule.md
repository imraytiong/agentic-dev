**Payload:**
We have updated the AI Bridge Protocol and the `SYSTEM_INSTRUCTIONS.md`. 

Because you are running remotely on the Mac Mini and Scribe is running locally, we are using Git as our transport layer. 

**New Rule:** Whenever you finish a task, write a message to `internal_ignore/inbox_scribe/`, commit, and push your branch, your message MUST explicitly state the name of the branch you just pushed. 

*(Example: "I have finished Phase 1. Pushed to branch: track-phase-1-interfaces").*

This makes it incredibly easy for the human to run `git fetch && git checkout <branch>` on their local machine to review your work.

Please acknowledge this new rule, and then proceed with executing Phase 1 of the BaseAgentChassis plan!