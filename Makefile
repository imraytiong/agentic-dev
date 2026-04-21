.PHONY: up down run-sandboxed test

# Default agent module fallback
AGENT ?= src.agents.hello_sparky.agent

up:
	docker compose up -d

down:
	docker compose down

# Architect & CTO Mandate: Strict environment injection and sandbox execution
# Refactored for Portability (No hardcoded absolute paths)
run-sandboxed:
	PYTHONPATH=src \
	ADK_ENV=mac_local \
	DB_HOST=localhost \
	REDIS_HOST=localhost \
	LITELLM_BUDGET=1.00 \
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	sandbox-exec \
		-D PROJECT_ROOT=$(shell pwd) \
		-D PYENV_ROOT=$(HOME)/.pyenv \
		-D VENV_PATH=$(shell pwd)/venv \
		-f infrastructure/mac_agent_sandbox.sb \
		venv/bin/python -m $(AGENT)

# Container Expert Mandate: Run tests OUTSIDE the sandbox to allow testcontainers 
# to access the OrbStack/Docker socket.
# CTO Mandate: Zero-friction testing with one command.
test:
	PYTHONPATH=src LITELLM_BUDGET=1.00 venv/bin/pytest tests/infrastructure/test_mac_mini_adapters.py -v
