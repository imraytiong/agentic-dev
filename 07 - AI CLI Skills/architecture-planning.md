# Skill: architecture-planning
**Description:** Guides users through a structured, iterative process for designing complex technical architectures, tracking decisions, and stress-testing designs.

## 📝 Note on Origin
This exact pattern was used to architect the Google ADK Distributed Microservice Chassis, which culminated in the creation of the `[Developer Guide](Agent%20Developers/Developer%20Guide.md)`. This process ensures that high-level abstract decisions are rigorously stress-tested and translated into a clean Developer Experience (DX).

## Step-by-Step Workflow

When activated, follow this exact sequence to guide the user through architectural design:

### 1. Establish Baselines & Constraints
Before designing anything, ask the user to define their non-negotiables.
- What is the primary framework or language? (e.g., Google ADK, Python strictly)
- What is the deployment target? (e.g., Docker Compose on Mac, K3s on Linux)
- What are the core design paradigms? (e.g., Distributed-First, No shared memory)
- *Action:* Do not proceed until these constraints are locked in. Record them in the system context.

### 2. Gap Analysis (The "Unprescribed" Zones)
Identify what the chosen framework *does not* do out of the box.
- For example, if using ADK, point out that it lacks native Long-Term Memory, Advanced RAG, or Observability backends.
- *Action:* Present a prioritized list of these gaps to the user and ask which one they want to tackle first.

### 3. Iterative Deep Dives (Options A/B/C)
For every architectural gap, never just ask "What do you want to do?" Instead, present 2-3 highly specific, technically viable options with clear Pros and Cons tailored to their constraints.
- *Example:* "For Long-Term Memory, since you want lightweight local deployment: Option A is PostgreSQL (relational only), Option B is pure Milvus (vector only), Option C is Postgres + pgvector (hybrid, single container)."
- *Action:* Wait for the user to select an option or request alternatives.

### 4. Maintaining the ADL (Architectural Decision Log)
Every time the user makes a choice in Step 3, you MUST document it.
- *Action:* Use the `write_file` or `append_content` tool to log the decision in a central `Architectural Decision Log.md` file. Include the decision, the rationale, and the alternatives rejected.

### 5. Tabletop Architecture (Stress-Testing)
Once the baseline decisions are made, force the user to trace a real-world scenario through the proposed architecture.
- *Action:* Present 2-3 hypothetical edge cases (e.g., "What happens if a task crashes halfway through?", "How do we identify the user across microservices?").
- *Goal:* Expose gaps in the design (like missing Dead Letter Queues or Auth Contexts) and immediately patch them using the Deep Dive (Step 3) method.

### 6. Defining the DX (Developer Experience)
Architecture is useless if it's too hard to use. The final step is translating the abstract decisions into concrete developer interfaces.
- *Action:* Draft the high-level code skeleton (e.g., the `BaseAgentChassis Reference`) showing exactly what methods the developer will call.
- *Action:* Review the skeleton and actively suggest abstractions to remove boilerplate (e.g., "Should we add a decorator to handle this queue listening automatically?").

## ⚠️ Core Directives
- **Never assume:** Always ask clarifying questions if the user's requirement is vague.
- **Enforce Constraints:** If the user chose "Lightweight/No-Cloud" in Step 1, do not suggest AWS DynamoDB in Step 3.
- **Document Relentlessly:** The output of this skill must be physical Markdown files outlining the decisions, not just chat history.