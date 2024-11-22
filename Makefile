.DEFAULT_GOAL := help
sources = src tests

.PHONY: .poetry  # Check that poetry is installed
.poetry:
	@poetry -V || echo 'Please install poetry https://python-poetry.org/'


.PHONY: .install-project
.install-project: .poetry # Install the package, dependencies, and pre-commit for local development
	poetry install --all-extras --sync

.PHONY: .install-pre-commit
.install-pre-commit: .poetry # Install the package, dependencies, and pre-commit for local development
	poetry run pre-commit install

.PHONY: format
format: .poetry # Auto-format Python source files
	poetry run black $(sources)
	poetry run isort $(sources)

.PHONY: lint
lint: .poetry # Lint python source files
	poetry run black $(sources) --check --diff
	poetry run isort $(sources) --check --diff
	poetry run flake8 $(sources)
	poetry run mypy $(sources)
	poetry run pre-commit run --all-files

.PHONY: test-cov
test-cov: .poetry # Run tests with coverage
	poetry run coverage erase
	poetry run pytest --cov=src --cov-report=xml

.PHONY: test
test: .poetry # Build packages for different versions of Python and run tests for each package
	poetry run pytest

PHONY: build
build: .poetry # Build the package
	poetry build

.PHONY: clean
clean: # Clean repository
	@rm -rf .mypy_cache
	@[ -f .coverage ] && rm .coverage || echo ".coverage doesn't exist"
	@rm -rf htmlcov
	@rm -rf dist

.PHONY: help # Show this help message (author @dwmkerr: https://dwmkerr.com/makefile-help-command/)
help: # (default) List all available commands
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY : all install
install : .install-project .install-pre-commit # Install the package, dependencies, and pre-commit for local development
all : clean install format lint test test-cov build# Run all commands
