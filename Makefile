.PHONY: up down run-sandboxed test

# Default arguments for run-sandboxed
ARGS ?= main.py

up:
	docker compose up -d

down:
	docker compose down

# Architect & CTO Mandate: Strict environment injection and sandbox execution
# Only used for running the agent in production-like local sandbox
run-sandboxed:
	PYTHONPATH=src \
	ADK_ENV=mac_local \
	DB_HOST=localhost \
	REDIS_HOST=localhost \
	LITELLM_BUDGET=1.00 \
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	sandbox-exec -D VENV_PATH=$(PWD)/venv -f infrastructure/mac_agent_sandbox.sb venv/bin/python -m src.agents.hello_sparky.agent

# Container Expert Mandate: Run tests OUTSIDE the sandbox to allow testcontainers 
# to access the OrbStack/Docker socket.
# CTO Mandate: Zero-friction testing with one command.
test:
	PYTHONPATH=src LITELLM_BUDGET=1.00 venv/bin/pytest tests/infrastructure/test_mac_mini_adapters.py -v
