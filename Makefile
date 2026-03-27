# 🔧 Prusa Connect Webcam Uploader - Development Makefile
# Provides convenient commands for development, testing, and deployment

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
RED := \033[31m
YELLOW := \033[33m
RESET := \033[0m

# Project variables
PROJECT_NAME := prusa-connect-webcam-uploader
PYTHON := python3
PIP := pip3
VENV_DIR := .venv
DOCKER_IMAGE := prusa-webcam-uploader
DOCKER_TAG := latest

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)🎥 Prusa Connect Webcam Uploader - Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*setup/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Development Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*dev/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Testing Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*test/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Docker Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*docker/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Other Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && !/setup|dev|test|docker/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# Setup commands
.PHONY: setup
setup: ## setup - Complete development environment setup
	@echo "$(BLUE)🔧 Setting up development environment...$(RESET)"
	$(MAKE) venv
	$(MAKE) install-deps
	$(MAKE) install-dev-deps
	$(MAKE) setup-env
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

.PHONY: venv
venv: ## setup - Create Python virtual environment
	@echo "$(BLUE)🐍 Creating virtual environment...$(RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✅ Virtual environment created in $(VENV_DIR)$(RESET)"
	@echo "$(YELLOW)💡 Activate with: source $(VENV_DIR)/bin/activate$(RESET)"

.PHONY: install-deps
install-deps: ## setup - Install production dependencies
	@echo "$(BLUE)📦 Installing production dependencies...$(RESET)"
	$(PIP) install -r requirements.txt

.PHONY: install-dev-deps
install-dev-deps: ## setup - Install development dependencies
	@echo "$(BLUE)🛠️ Installing development dependencies...$(RESET)"
	$(PIP) install -r test_requirements.txt

.PHONY: setup-env
setup-env: ## setup - Create .env file from template
	@if [ ! -f .env ]; then \
		echo "$(BLUE)⚙️ Creating .env file from template...$(RESET)"; \
		cp .env.template .env; \
		echo "$(GREEN)✅ .env file created$(RESET)"; \
		echo "$(YELLOW)💡 Edit .env with your actual credentials$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️ .env file already exists$(RESET)"; \
	fi

# Development commands
.PHONY: dev
dev: ## dev - Run application in development mode
	@echo "$(BLUE)🚀 Starting application in development mode...$(RESET)"
	PYTHONLOGLEVEL=DEBUG $(PYTHON) prusa_webcam_uploader.py

.PHONY: check
check: ## dev - Run all code quality checks
	@echo "$(BLUE)🧹 Running code quality checks...$(RESET)"
	python run_tests.py --lint-only

.PHONY: format
format: ## dev - Format code with black and isort
	@echo "$(BLUE)🎨 Formatting code...$(RESET)"
	black prusa_webcam_uploader.py --line-length 100
	isort prusa_webcam_uploader.py
	@echo "$(GREEN)✅ Code formatting completed$(RESET)"

.PHONY: lint
lint: ## dev - Run linting with flake8
	@echo "$(BLUE)🔍 Running linter...$(RESET)"
	flake8 prusa_webcam_uploader.py --max-line-length=100 --ignore=E501,W503,E203

.PHONY: typecheck
typecheck: ## dev - Run type checking with mypy
	@echo "$(BLUE)🔍 Running type checker...$(RESET)"
	mypy prusa_webcam_uploader.py --ignore-missing-imports --no-strict-optional

.PHONY: security
security: ## dev - Run security check with bandit
	@echo "$(BLUE)🔒 Running security check...$(RESET)"
	bandit -r prusa_webcam_uploader.py

# Testing commands
.PHONY: test
test: ## test - Run all tests
	@echo "$(BLUE)🧪 Running test suite...$(RESET)"
	python run_tests.py

.PHONY: test-unit
test-unit: ## test - Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	python run_tests.py --quick

.PHONY: test-performance
test-performance: ## test - Run performance tests
	@echo "$(BLUE)📊 Running performance tests...$(RESET)"
	python run_tests.py --perf-only

.PHONY: test-coverage
test-coverage: ## test - Run tests with coverage report
	@echo "$(BLUE)📊 Running tests with coverage...$(RESET)"
	python run_tests.py --coverage
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/index.html$(RESET)"

.PHONY: test-watch
test-watch: ## test - Run tests in watch mode
	@echo "$(BLUE)👀 Running tests in watch mode...$(RESET)"
	pytest-watch

# Docker commands
.PHONY: docker-build
docker-build: ## docker - Build Docker image
	@echo "$(BLUE)🐋 Building Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✅ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(RESET)"

.PHONY: docker-run
docker-run: ## docker - Run Docker container
	@echo "$(BLUE)🐋 Running Docker container...$(RESET)"
	docker run --rm -it \
		--env-file .env \
		--add-host=host.docker.internal:host-gateway \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker-dev
docker-dev: ## docker - Run Docker container in development mode
	@echo "$(BLUE)🐋 Running Docker container in development mode...$(RESET)"
	docker run --rm -it \
		--env-file .env \
		-e PYTHONLOGLEVEL=DEBUG \
		--add-host=host.docker.internal:host-gateway \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker-compose-up
docker-compose-up: ## docker - Start services with docker-compose
	@echo "$(BLUE)🐙 Starting services with docker-compose...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services started$(RESET)"
	@echo "$(YELLOW)💡 View logs with: make docker-logs$(RESET)"

.PHONY: docker-compose-down
docker-compose-down: ## docker - Stop services with docker-compose
	@echo "$(BLUE)🐙 Stopping services with docker-compose...$(RESET)"
	docker-compose down

.PHONY: docker-logs
docker-logs: ## docker - View Docker container logs
	@echo "$(BLUE)📜 Viewing Docker logs...$(RESET)"
	docker-compose logs -f prusa-webcam-uploader

.PHONY: docker-shell
docker-shell: ## docker - Open shell in running container
	@echo "$(BLUE)🐋 Opening shell in container...$(RESET)"
	docker exec -it prusa-webcam-uploader bash

.PHONY: docker-clean
docker-clean: ## docker - Clean up Docker images and containers
	@echo "$(BLUE)🧹 Cleaning up Docker resources...$(RESET)"
	docker-compose down --rmi all --volumes --remove-orphans
	docker image prune -f
	@echo "$(GREEN)✅ Docker cleanup completed$(RESET)"

# Documentation
.PHONY: docs
docs: ## Generate documentation
	@echo "$(BLUE)📚 Generating documentation...$(RESET)"
	@echo "$(YELLOW)💡 Documentation is maintained manually$(RESET)"
	@echo "$(YELLOW)💡 See docs/ directory for all documentation$(RESET)"

# Release commands
.PHONY: release-check
release-check: ## Check if ready for release
	@echo "$(BLUE)🔍 Checking release readiness...$(RESET)"
	$(MAKE) check
	$(MAKE) test
	@echo "$(GREEN)✅ Ready for release!$(RESET)"

.PHONY: bump-version
bump-version: ## Bump version (requires VERSION variable)
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)❌ VERSION variable required. Example: make bump-version VERSION=1.1.0$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📈 Bumping version to $(VERSION)...$(RESET)"
	sed -i '' 's/__version__ = ".*"/__version__ = "$(VERSION)"/' prusa_webcam_uploader.py
	@echo "$(GREEN)✅ Version bumped to $(VERSION)$(RESET)"

# Utility commands
.PHONY: clean
clean: ## Clean up temporary files
	@echo "$(BLUE)🧹 Cleaning up temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

.PHONY: reset
reset: clean ## Reset development environment
	@echo "$(BLUE)🔄 Resetting development environment...$(RESET)"
	rm -rf $(VENV_DIR)
	rm -f .env
	@echo "$(GREEN)✅ Environment reset$(RESET)"
	@echo "$(YELLOW)💡 Run 'make setup' to recreate$(RESET)"

.PHONY: info
info: ## Show project information
	@echo "$(BLUE)📋 Project Information$(RESET)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Pip: $(shell $(PIP) --version)"
	@echo "  Docker: $(shell docker --version 2>/dev/null || echo 'Not installed')"
	@echo "  Git: $(shell git --version)"
	@echo ""
	@echo "$(BLUE)📁 Project Structure$(RESET)"
	@echo "  Virtual Env: $(VENV_DIR) $(shell [ -d $(VENV_DIR) ] && echo '✅' || echo '❌')"
	@echo "  .env file: $(shell [ -f .env ] && echo '✅' || echo '❌')"
	@echo "  Dependencies: $(shell [ -f requirements.txt ] && echo '✅' || echo '❌')"
	@echo ""

.PHONY: validate-env
validate-env: ## Validate environment configuration
	@echo "$(BLUE)🔍 Validating environment configuration...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ .env file not found$(RESET)"; \
		exit 1; \
	fi
	@if ! grep -q "FINGERPRINT=" .env; then \
		echo "$(RED)❌ FINGERPRINT not set in .env$(RESET)"; \
		exit 1; \
	fi
	@if ! grep -q "TOKEN=" .env; then \
		echo "$(RED)❌ TOKEN not set in .env$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Environment configuration valid$(RESET)"

# CI/CD simulation
.PHONY: ci
ci: ## Simulate CI/CD pipeline locally
	@echo "$(BLUE)🚀 Simulating CI/CD pipeline...$(RESET)"
	$(MAKE) clean
	$(MAKE) install-deps
	$(MAKE) install-dev-deps
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) security
	$(MAKE) test
	$(MAKE) docker-build
	@echo "$(GREEN)✅ CI/CD simulation completed successfully!$(RESET)"

# Aliases for convenience
.PHONY: install
install: install-deps ## Alias for install-deps

.PHONY: run
run: dev ## Alias for dev

.PHONY: build
build: docker-build ## Alias for docker-build

.PHONY: up
up: docker-compose-up ## Alias for docker-compose-up

.PHONY: down
down: docker-compose-down ## Alias for docker-compose-down

.PHONY: logs
logs: docker-logs ## Alias for docker-logs
