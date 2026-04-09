# Standard Agentic Workflows

**Tags:** #architecture #patterns #workflows #adk

This document outlines the standard architectural patterns we will use when designing agents on top of our `BaseAgentChassis` and the Google Agent Development Kit (ADK). By standardizing these workflows, we ensure consistency, predictability, and easier debugging across our distributed fleet.

---

## 1. The Supervisor / Router Pattern (The Front Door)

**The Concept:** 
The user never interacts directly with a heavy, slow, specialized agent. Instead, all requests hit a Supervisor agent. The Supervisor's sole responsibility is to understand the user's intent, extract any necessary parameters, and route the task to the correct specialist agent in the cluster.

**Implementation Strategy (The Hybrid Approach):**
We use a hybrid routing architecture to balance speed, cost, and flexibility:
1.  **Phase 1: Deterministic Semantic Routing.** The user's prompt is embedded and compared against a predefined list of "Agent Capabilities" stored in `pgvector`. If the confidence score is high (e.g., > 90%), the `BaseAgentChassis` routes the request instantly using standard Python logic. This saves LLM tokens and drastically reduces latency for common requests.
2.  **Phase 2: LLM Fallback.** If the semantic confidence score is low (an ambiguous or complex edge-case request), the request is passed to a fast, lightweight LLM (e.g., Gemini 1.5 Flash). The LLM uses its reasoning capabilities to evaluate the available routing tools and make a dynamic decision.

**Chassis Integration:** 
The Supervisor uses `await self.call_agent_sync()` for quick data retrievals or `await self.publish_async_task()` to drop massive jobs onto a specialist's queue.

---

## 2. The Plan-and-Execute Pattern (For Complex Tasks)

**The Concept:** 
When a user asks a multi-step, complex question (e.g., "Analyze Q3 financials and compare them to competitor SEC filings"), standard ReAct agents often get confused, lose context, or get stuck in infinite tool loops. This pattern splits the cognitive load.

**Implementation Strategy:**
1.  **The Planner (Agent A):** Takes the high-level goal and generates a strict, linear JSON array of steps required to solve it. It does not execute tools.
2.  **The Executor (Agent B):** Takes the plan step-by-step. It executes the necessary tools for Step 1, saves the intermediary result to long-term memory via `self.save_state()`, and then moves to Step 2.

**Chassis Integration:** 
We can leverage ADK's native `SequentialAgent` primitive, wrapping it within our chassis to ensure state is persisted to PostgreSQL between steps.

---

## 3. The Evaluator-Optimizer Pattern (The "Ralph Loop")

**The Concept:** 
LLMs hallucinate and make mistakes. For high-stakes outputs (like writing code, drafting external emails, or formatting strict JSON), we do not return the first draft. We send it to a critic.

**Implementation Strategy:**
1.  **The Drafter:** Generates the initial output or code.
2.  **The Evaluator:** Reviews the output against specific criteria or runs a deterministic Python test tool against it.
3.  **The Loop:** If the output fails the evaluation/test, the Evaluator feeds the specific error message back to the Drafter. The Drafter attempts to fix it. This loops until the test passes or a maximum retry limit is reached.

**Chassis Integration:** 
We use ADK's native `LoopAgent` primitive to handle the cyclic reasoning, utilizing the chassis to log custom metrics (`self.record_metric()`) on how many retries were required, giving us observability into prompt degradation.