---
name: adr-manager
description: Standardizes the creation, tracking, and formatting of Architectural Decision Records (ADRs) and maintains the Master Decision Log.
---

# Architectural Decision Record (ADR) Manager

This skill defines the standard operating procedure for capturing, logging, and tracking architectural decisions within the agent development vault.

## 1. The Master Log
Always maintain the `03 - Architecture & Patterns/Architectural Decision Log.md` file. This file acts as the single source of truth for:
- **Approved Decisions:** What we decided and why.
- **Pending/Open Questions:** Topics that require deep dives before a decision is reached.

## 2. ADR Format
When creating a dedicated note for a complex architectural decision, use the following structure:
```markdown
# ADR: [Topic Name]

**Date:** YYYY-MM-DD
**Status:** [Proposed | Deep Dive | Approved | Rejected | Deprecated]
**Tags:** #adr #architecture

## 1. Context & Problem Statement
What is the specific issue or gap we are trying to solve?

## 2. Considered Options
- Option A (Pros/Cons)
- Option B (Pros/Cons)

## 3. Decision Outcome
What did we choose and why? (Provide specific rationale).

## 4. Consequences
- **Positive:** What do we gain?
- **Negative:** What technical debt or constraints do we accept?
```

## 3. Workflow
1. When the user introduces a new architectural gap, add it to the "Pending Decisions" section of the Master Log.
2. Deep dive into the topic with the user. Ask probing technical questions one at a time.
3. Once the user is satisfied, formally write the decision into the Master Log (and optionally an ADR note) and mark it as "Approved".
4. Prompt the user to select the next pending decision to deep dive into.