# ==============================================================================
# STEERBOT PLATFORM: AUTOMATION CONTROL PLANE
# ==============================================================================
# "Makefiles are the universal API for build engineering."
# ==============================================================================

# Variables
DOCKER_COMPOSE = docker-compose
SERVICE_NAME = steerbot-control
IMAGE_TAG = latest

.PHONY: help build up down logs shell clean test

help: ## Show this help message
	@echo "Steerbot DevOps Automation - Available Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the operational containers (Multi-stage)
	@echo "[BUILD] Compiling ROS 2 Workspace in Docker..."
	$(DOCKER_COMPOSE) build

up: ## Start the Control Plane (Detached)
	@echo "[DEPLOY] Launching Steerbot Control Plane..."
	$(DOCKER_COMPOSE) up -d $(SERVICE_NAME)

down: ## Stop and remove containers
	@echo "[STOP] Teardown active sessions..."
	$(DOCKER_COMPOSE) down

logs: ## Stream logs from the Control Plane
	$(DOCKER_COMPOSE) logs -f $(SERVICE_NAME)

shell: ## Open a bash shell inside the running container (for debugging)
	@echo "[DEBUG] Attaching to container shell..."
	$(DOCKER_COMPOSE) exec $(SERVICE_NAME) /bin/bash

clean: ## Prune Docker artifacts
	@echo "[CLEAN] Removing dangling images and build cache..."
	docker system prune -f

test: ## Run unit tests inside the container
	@echo "[TEST] Executing maneuver verification..."
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) python3 maneuver_control.py --dry-run
