**To: AI CLI**
**From: CTO & Architect Lead**
**Subject: Package Repo as "ADK Harness" SDK**

We are transitioning this repository from a monolithic project into a reusable Software Development Kit (SDK) named **ADK Harness**. Future agent repositories will `pip install` this repository directly via Git.

Please execute the following packaging steps:

### 1. Create `pyproject.toml`
Create a standard `pyproject.toml` at the root of the repository. 
- **Name:** `adk-harness`
- **Version:** `0.1.0`
- **Dependencies:** Extract all the core dependencies required by the chassis and adapters (e.g., `pydantic`, `litellm`, `asyncpg`, `redis`, `pgvector`) and list them here.
- **Build System:** Use `setuptools`. Configure it to find packages inside the `src/` directory (e.g., `universal_core`, `infrastructure`, `agents`).

### 2. Create `__init__.py` files
Ensure that `src/`, `src/universal_core/`, and `src/infrastructure/` have the necessary `__init__.py` files so Python recognizes them as exportable modules.

### 3. Verification
Run a quick diagnostic to ensure that if someone runs `pip install -e .` in the root directory, the `universal_core` and `infrastructure` modules are successfully installed into their local environment.

**Do not alter the Makefile, the Sandbox, or the Adapters.** We are strictly adding the packaging metadata.
