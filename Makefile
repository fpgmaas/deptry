.PHONY: install
install: ## Install the PDM environment.
	@echo "🚀 Creating virtual environment using PDM"
	@pdm install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking PDM lock file consistency with 'pyproject.toml': Running pdm lock --check"
	@pdm lock --check
	@echo "🚀 Linting code: Running pre-commit"
	@pdm run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@pdm run mypy
	@echo "🚀 Checking for dependency issues: Running deptry"
	@pdm run deptry python

.PHONY: test
test: test-unit test-functional

.PHONY: test-unit
test-unit: ## Run unit tests.
	@echo "🚀 Running unit tests"
	@pdm run pytest tests/unit

.PHONY: test-functional
test-functional: ## Run functional tests.
	@echo "🚀 Running functional tests"
	@pdm run pytest tests/functional -n auto --dist loadgroup

.PHONY: build
build: ## Build wheel and sdist files using PDM.
	@echo "🚀 Creating wheel and sdist files"
	@maturin build

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors.
	@pdm run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation.
	@pdm run mkdocs serve

.PHONY: help
help: ## Show help for the commands.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
