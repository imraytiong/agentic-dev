# Architecture Planning & Design

This skill provides a structured, iterative workflow for designing complex system architectures, identifying technical gaps, and making strategic engineering decisions.

## 📝 Note on Origin
This exact pattern was used to architect the Google ADK Distributed Microservice Chassis, which culminated in the creation of the `[Developer Guide](Developer%20Guide.md)`. This process ensures that high-level abstract decisions are rigorously stress-tested and translated into a clean Developer Experience (DX).

## Step-by-Step Workflow

### Step 1: Establish Baselines & Constraints
Before making any decisions, explicitly define the non-negotiable constraints.
- **Identify the Core Framework:** What is the primary tool/language? (e.g., Python, Google ADK).
- **Define Guiding Principles:** (e.g., "Open Source First", "Distributed-First", "Lightweight").
- **Target Infrastructure:** Where will this run? (e.g., Mac Mini, K3s, Cloud Run).

### Step 2: Gap Analysis (The "Unprescribed" Zones)
Identify what the core framework does *not* do out of the box. Create a "Deep Dive Queue" of these gaps.
Common gaps include:
- State & Long-Term Memory Persistence
- Inter-service Communication (Sync vs. Async)
- Observability & Tracing
- Testing & Evaluation
- Deployment & Orchestration

### Step 3: Iterative Deep Dives (One at a Time)
Do not overwhelm the user with 10 decisions at once. Tackle the Deep Dive Queue one item at a time.
1. Present the problem.
2. Provide 2-4 distinct architectural options (Option A, Option B, etc.).
3. Clearly list the **Pros and Cons** of each option, specifically filtering them through the constraints established in Step 1.
4. Provide a "Technical Lead Recommendation."
5. Wait for the user to decide.

### Step 4: Maintain the Architectural Decision Log (ADL)
As soon as a decision is made, officially log it in a central `Architectural Decision Log` file.
- Record the decision and the *rationale* behind it.
- Keep a visible "Pending Decisions" queue at the bottom of the ADL.

### Step 5: Tabletop Architecture (Stress Testing)
Once the high-level architecture is defined, try to break it.
1. Design 3 distinct, real-world scenarios or execution paths.
2. Trace the data through the proposed architecture step-by-step.
3. Identify **Architectural Gaps** (e.g., "Wait, how does Agent B know which user triggered Agent A?").
4. Propose solutions (e.g., "Implement an `AgentContext` wrapper") and update the ADL.

### Step 6: Define the Developer Experience (DX)
Translate the abstract architecture into concrete developer interfaces.
- Draft the core interfaces, classes, or boilerplate skeletons.
- Create a `Developer Guide` with practical code samples showing how a developer will actually interact with the architecture on a daily basis.

## Edge Cases & Rules
- **Never jump ahead:** If the user wants to stay on a specific topic (e.g., Database schemas) until they are satisfied, do not force them to move to the next item in the queue.
- **Portability:** Always consider how the architecture behaves locally (for testing) versus in production.
- **Guardrails:** When designing the DX, build "guardrails" (like strict types or decorators) that prevent developers or AI coding tools from accidentally violating the architectural constraints.