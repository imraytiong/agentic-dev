# AI Bridge Protocol: Sandbox Portability & Makefile Upgrades

**To:** AI CLI Agent
**Context:** The Mac Mini infrastructure is fully operational, but the developer experience and portability need a final layer of polish before we close out the track.

**Objective:** Refactor the `Makefile` and `mac_agent_sandbox.sb` to eliminate hardcoded absolute paths, and update the `Makefile` to securely run *any* agent module dynamically.

### Mandates:

**1. Make the Sandbox 100% Portable (No Hardcoded Paths)**
The `mac_agent_sandbox.sb` currently hardcodes `/Users/raytiongai/projects/agentic-dev` and `/Users/raytiongai/.pyenv`. This breaks if the folder is moved.
*   **Action:** Update the `Makefile`'s `run-sandboxed` target to dynamically calculate and pass these paths using the `-D` flag:
    *   `-D PROJECT_ROOT=$(shell pwd)`
    *   `-D PYENV_ROOT=$(HOME)/.pyenv`
*   **Action:** Update `infrastructure/mac_agent_sandbox.sb` to replace the hardcoded strings with `(param "PROJECT_ROOT")` and `(param "PYENV_ROOT")`. 
*   **Action:** In the `file-write*` section of the `.sb` file, use `(string-append (param "PROJECT_ROOT") "/.data")` and `(string-append (param "PROJECT_ROOT") "/tmp")` to dynamically construct the write boundaries.

**2. Universal Agent Execution**
The `Makefile` currently hardcodes the execution of `python main.py` or a specific agent module.
*   **Action:** Update the `Makefile` to accept an `AGENT` variable.
*   **Action:** Set a default fallback: `AGENT ?= src.agents.hello_sparky.agent`.
*   **Action:** Update the execution command to run: `python -m $(AGENT)`.
*   **Action:** Ensure all required credentials (`POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`) are explicitly passed in the `run-sandboxed` execution block so the IoC container doesn't throw a `ValueError`.

**Output:**
Execute these refactors on the `feat/mac-mini-infra` branch. Report back when the `Makefile` and sandbox profile are fully portable.