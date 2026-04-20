.PHONY: up down run-sandboxed

# Default arguments for run-sandboxed
ARGS ?= main.py

up:
	docker compose up -d

down:
	docker compose down

# Architect & CTO Mandate: Strict environment injection and sandbox execution
run-sandboxed:
	ADK_ENV=mac_local \
	DB_HOST=localhost \
	REDIS_HOST=localhost \
	LITELLM_BUDGET=1.00 \
	sandbox-exec -f infrastructure/mac_agent_sandbox.sb python $(ARGS)
