PROJECT ?= {{cookiecutter.project_slug}}
VERSION ?= $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
PYTHON_VERSION = $(shell grep 'python =' pyproject.toml | sed -n 's/^python = ["^]*\([0-9]*\.[0-9]*\)\(.*\)"/\1/p')

.PHONY: test fmt lint mypy clean help version release

version: ## Show the current version
	echo "Current version: $(VERSION)"

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort |\
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL=help

.python-version: ## Installs the correct version of python if required
	$(if $(shell pyenv versions --bare | grep "^$(PYTHON_VERSION)"),, pyenv install $(PYTHON_VERSION))
	pyenv local $(shell pyenv versions --bare | grep "^$(PYTHON_VERSION)" | tail -n 1)

.venv: .python-version ## Activates and installs the poetry environment.
	poetry env use ~/.pyenv/versions/$(shell cat $<)/bin/python && \
	poetry install

lint: .venv ## Lint the project
	poetry run flake8

mypy: .venv ## Run mypy
	poetry run mypy

test: .venv ## Test the project
	poetry run pytest

fmt: .venv ## Run formatting tools for project
	poetry run black . $(if $(CI),--check ,) && poetry run isort . $(if $(CI),--check ,)

bandit: .venv ## Run bandit
	poetry run bandit -c pyproject.toml -r .

check: fmt lint mypy bandit test ; ## Run all checks

clean: ## Clean the project
	rm -rf .venv
	rm -rf .python-version
	rm -rf dist/
	rm -rf __pycache__ **/__pycache__ **/**/__pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf .poetry

requirements.txt:
	poetry export --without-hashes --format $@ --output $@

release: requirements.txt ## Build Lambda Release Artifact
	poetry run pip install . -r requirements.txt --target dist/$(PROJECT)
	cd dist/$(PROJECT) && zip --exclude '*__pycache__*' '*.pyc' -r ../application.zip .
