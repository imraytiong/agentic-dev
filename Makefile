.PHONY: up down run-sandboxed test test-e2e

# Include .env file if it exists, otherwise rely on environment variables
-include .env
export

# Default agent module fallback
AGENT ?= src.agents.hello_sparky.agent

# Dynamic resolution of paths for the portable sandbox
PROJECT_ROOT ?= $(shell pwd)
PYENV_ROOT ?= $(HOME)/.pyenv

# Container Expert Mandate: Auto-Venv Activation
ifdef VIRTUAL_ENV
    VENV_PATH ?= $(VIRTUAL_ENV)
else
    VENV_PATH ?= $(PROJECT_ROOT)/venv
endif

up:
	docker compose up -d

down:
	docker compose down

# Architect & CTO Mandate: Strict environment injection and sandbox execution
run-sandboxed:
	PYTHONPATH=src \
	ADK_ENV=mac_local \
	DB_HOST=localhost \
	REDIS_HOST=localhost \
	LITELLM_BUDGET=1.00 \
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	GEMINI_API_KEY=$(GEMINI_API_KEY) \
	sandbox-exec \
		-D PROJECT_ROOT=$(PROJECT_ROOT) \
		-D PYENV_ROOT=$(PYENV_ROOT) \
		-D VENV_PATH=$(VENV_PATH) \
		-f ops/mac_local/mac_agent_sandbox.sb \
		$(VENV_PATH)/bin/python -m $(AGENT)

# Container Expert Mandate: Run tests OUTSIDE the sandbox to allow testcontainers 
# to access the OrbStack/Docker socket.
test:
	PYTHONPATH=src LITELLM_BUDGET=1.00 $(VENV_PATH)/bin/pytest tests/infrastructure/test_mac_mini_adapters.py -v

# CTO & Test Lead Mandate: Dynamic E2E Target with Mock Default
# Runs Franky diagnostic agent
ADK_ENV ?= mock

ifeq ($(ADK_ENV),mac_local)
test-e2e:
	PYTHONPATH=src \
	ADK_ENV=$(ADK_ENV) \
	DB_HOST=localhost \
	REDIS_HOST=localhost \
	LITELLM_BUDGET=1.00 \
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	GEMINI_API_KEY=$(GEMINI_API_KEY) \
	sandbox-exec \
		-D PROJECT_ROOT=$(PROJECT_ROOT) \
		-D PYENV_ROOT=$(PYENV_ROOT) \
		-D VENV_PATH=$(VENV_PATH) \
		-f ops/mac_local/mac_agent_sandbox.sb \
		$(VENV_PATH)/bin/python -m src.agents.franky.agent
else
test-e2e:
	PYTHONPATH=src \
	ADK_ENV=$(ADK_ENV) \
	$(VENV_PATH)/bin/python -m src.agents.franky.agent
endif
