.PHONY: up down run-sandboxed test

# 2. Implement the "Dumb" Makefile
# Include .env file if it exists, otherwise rely on environment variables
-include .env
export

# Default agent module fallback
AGENT ?= src.agents.hello_sparky.agent

# Dynamic resolution of paths for the portable sandbox
PROJECT_ROOT ?= $(shell pwd)
PYENV_ROOT ?= $(HOME)/.pyenv
VENV_PATH ?= $(PROJECT_ROOT)/venv

up:
	docker compose up -d

down:
	docker compose down

# Architect & CTO Mandate: Strict environment injection and sandbox execution
# Refactored for Portability (No hardcoded absolute paths)
run-sandboxed:
	PYTHONPATH=src \
	sandbox-exec \
		-D PROJECT_ROOT=$(PROJECT_ROOT) \
		-D PYENV_ROOT=$(PYENV_ROOT) \
		-D VENV_PATH=$(VENV_PATH) \
		-f ops/mac_local/mac_agent_sandbox.sb \
		$(VENV_PATH)/bin/python -m $(AGENT)

# Container Expert Mandate: Run tests OUTSIDE the sandbox to allow testcontainers 
# to access the OrbStack/Docker socket.
# CTO Mandate: Zero-friction testing with one command.
test:
	PYTHONPATH=src venv/bin/pytest tests/infrastructure/test_mac_mini_adapters.py -v
