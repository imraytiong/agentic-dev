# Fix `.env.template` for Studio UI

**Context:** 
We recently implemented the "Production Kill Switch" (Safe Defaults Protocol) making `ENABLE_STUDIO=False` the default for the `BaseAgentChassis`. However, the `.env.template` (or `.env.example`) file used for local development and out-of-the-box prototyping currently has it disabled by default too. 

For local development and codelabs, we want the Agent Studio to be enabled by default.

**Instructions:**
1. Locate the `.env.template` (or `.env.example`) file at the root of the repository.
2. Update the file to explicitly include:
   ```env
   # Enable Agent Studio Web UI for local development
   ENABLE_STUDIO=true
   ```
3. If there are any other `.env` template files used for developer onboarding, ensure they also have `ENABLE_STUDIO=true`.
4. Commit the changes to the `feat/mac-mini-infra` branch.

Once completed, report back.