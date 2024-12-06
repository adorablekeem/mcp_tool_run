# {{cookiecutter.project_name}}

This repository contains a Python project setup with various Make targets to facilitate development tasks such as linting, type checking, testing, and formatting.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/)
- Make

Ensure Docker is running if you're executing Docker-based commands.

## Setup

To set up the project, first clone the repository and then install the dependencies using Poetry:

```bash
poetry install
```

## Make Targets

The repository includes the following Make targets for ease of development:

### Linting

To lint the project and check for any coding style issues, run:

```bash
make lint
```

This uses `flake8` for linting.

### Type Checking

To run type checking with `mypy`, use:

```bash
make mypy
```

### Testing

To execute the project's tests, run:

```bash
make test
```

This command uses `pytest` to run tests.

### Formatting

To format the project files, run:

```bash
make fmt
```

This will run `black` for code formatting and `isort` for import sorting. If the `CI` environment variable is set, it will only check for formatting without applying changes.

### Security Scanning

To scan the project for common security issues, use:

```bash
make bandit
```

This command runs `bandit` with a configuration specified in `pyproject.toml`.

### Running All Checks

To run formatting, linting, type checking, security scanning, and tests all together, use:

```bash
make check
```

### Cleaning

To clean the project directory from build artifacts and caches, you can use:

```bash
make clean
```

This will remove `dist/`, `__pycache__/`, and `.pytest_cache/` directories.


### Continuous Integration (CI)

This project uses [Buildkite](https://buildkite.com/) for Continuous Integration (CI). The CI pipeline is defined in `.buildkite/pipeline.yml` and automates running the above checks on each push to the repository, ensuring that code changes meet quality standards before they are merged.
