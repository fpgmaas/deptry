install: ## Install the poetry environment
	@echo "🚀 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry shell

check: ## Lint code using pre-commit and check obsolete dependencies using deptry.
	@echo "🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry lock --check
	@echo "🚀 Linting code: Running pre-commit"
	@pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@deptry .

test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@pytest --cov --cov-config=pyproject.toml --cov-report=xml

build: clean-build ## Build wheel file using poetry
	@echo "🚀 Creating wheel file"
	@poetry build

clean-build: ## clean build artifacts
	@rm -rf dist

publish: ## publish a release to pypi.
	@echo "🚀 Publishing: Dry run."
	@poetry config pypi-token.pypi $(PYPI_TOKEN)
	@poetry publish --dry-run
	@echo "🚀 Publishing."
	@poetry publish

build-and-publish: build publish ## Build and publish.

docs-test: ## Test if documentation can be built without warnings or errors
	@( cd docs ; poetry run mkdocs build -s)

docs: ## Build and serve the documentation
	@( cd docs ; poetry run mkdocs serve )

.PHONY: docs

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help