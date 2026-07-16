# Makefile
# Useful commands

ENV_NAME := pptagent
CONDA_ACTIVATE := eval "$$(conda shell.bash hook)" && conda activate $(ENV_NAME)

.PHONY: help install test lint format clean docs

help:  ## helper
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## create conda env from environment.yml
	@echo "Creating conda env: $(ENV_NAME)..."
	conda env create -f environment.yml -n $(ENV_NAME) || \
		(echo "Environment updating..." && conda env update -f environment.yml -n $(ENV_NAME) --prune)
	@echo "Installing dependencies..."
	bash -c "$(CONDA_ACTIVATE) && pip install -e . --no-deps"
	@echo "Installing pre-commit hooks..."
	bash -c "$(CONDA_ACTIVATE) && pre-commit install"
	@echo "Installed! To check env, run 'make verify'."
	@echo "To activate env, run 'conda activate $(ENV_NAME)'"

install-fresh:  ## uninstall old env and reinstall.
	-conda env remove -n $(ENV_NAME) -y
	conda env create -f environment.yml -n $(ENV_NAME)
	bash -c "$(CONDA_ACTIVATE) && pip install -e . --no-deps"
	bash -c "$(CONDA_ACTIVATE) && pre-commit install"
	@echo "Env refreshed!"

test:  ## run all tests
	bash scripts/run_tests.sh

test-fast:  ## quick run-loop-test
	bash -c "$(CONDA_ACTIVATE) && pytest -v -m 'not slow and not integration' tests/"

lint:  ## code sanity check
	bash scripts/run_lint.sh

format:  ## format code
	bash -c "$(CONDA_ACTIVATE) && ruff format pptagent/ tests/"
	bash -c "$(CONDA_ACTIVATE) && ruff check --fix pptagent/ tests/"
	bash -c "$(CONDA_ACTIVATE) && isort pptagent/ tests/"

typecheck:  ## type check
	bash -c "$(CONDA_ACTIVATE) && mypy pptagent/"

verify:  ## env validation check
	bash -c "$(CONDA_ACTIVATE) && python scripts/verify_deps.py"

clean:  ## clean temp files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf docs/coverage coverage.xml
	rm -rf dist build
	bash scripts/clean.sh

docs:  ## make a doc
	bash -c "$(CONDA_ACTIVATE) && mkdocs build"

docs-serve:  ## run a local doc server
	bash -c "$(CONDA_ACTIVATE) && mkdocs serve"

shell:  ## IPython Shell
	bash -c "$(CONDA_ACTIVATE) && ipython -c \"import pptagent; print(f'PPTAgent {pptagent.__version__}')\" -i"

lock:  ## env snapshot
	conda env export -n $(ENV_NAME) > environment-lock.yml
	@echo "Env snapshot saved to environment-lock.yml"

env-remove:  ## env remove
	conda env remove -n $(ENV_NAME) -y
	@echo "Environment $(ENV_NAME) removed"

check-all: lint test  ## env check
