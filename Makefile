.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help setup build up down restart logs shell ps clean rebuild

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: ## First-time setup: create .env from the example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env — now edit it and add your GEMINI_API_KEY."; \
	else \
		echo ".env already exists, nothing to do."; \
	fi

build: ## Build the Docker image
	$(COMPOSE) build

up: ## Start the app (detached) at http://localhost:8000
	$(COMPOSE) up -d

up-build: ## Build and start the app
	$(COMPOSE) up -d --build

down: ## Stop and remove containers
	$(COMPOSE) down

restart: ## Restart the app
	$(COMPOSE) restart

logs: ## Tail application logs
	$(COMPOSE) logs -f

shell: ## Open a shell inside the running container
	$(COMPOSE) exec app /bin/bash

ps: ## Show running containers
	$(COMPOSE) ps

rebuild: ## Rebuild from scratch (no cache) and start
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

clean: ## Stop containers and remove image + volumes
	$(COMPOSE) down --rmi local --volumes
