.DEFAULT_GOAL := all
sources = src tests

.PHONY: .poetry  # Check that poetry is installed
.poetry:
	@poetry -V || echo 'Please install poetry https://python-poetry.org/'

.PHONY: .pre-commit  # Check that pre-commit is installed
.pre-commit:
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

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

.PHONY: pre-commit
pre_commit: .poetry # Run pre-commit for all files
	poetry run pre-commit run --all-files

.PHONY: test-cov
test-cov: .poetry .clean-coverage # Run tests with coverage
	poetry run tox run -e testcov

.PHONY: test
test: .poetry # Build packages for different versions of Python and run tests for each package
	poetry run tox run -e py39,py310,py311

.PHONY: .clean-coverage  # Remove coverage reports and files
.clean-coverage:
	@[ -f .coverage ] && rm .coverage || echo ".coverage doesn't exist"
	@rm -rf htmlcov

.PHONY: .clean-build
.clean-build:
	@rm -rf dist

PHONY: build
build: .poetry .clean-build # Build the package
	poetry build

.PHONY: clean
clean: .clean-coverage .clean-build# Clean repository
	@rm -rf .tox
	@rm -rf .mypy_cache

.PHONY: help # Show this help message (author @dwmkerr: https://dwmkerr.com/makefile-help-command/)
help: # (default) List all available commands
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY : init-local, init-remote, all
install : .install-project .install-pre-commit # Install the package, dependencies, and pre-commit for local development
install-cicd : .install-project # Install the package, dependencies, and pre-commit for cicd
all : clean install format lint pre_commit test test-cov build# Run all commands
