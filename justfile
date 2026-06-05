set shell := ["bash", "-euo", "pipefail", "-c"]

setup:
	@echo "Python dependencies are provided by the declarative workstation; no repo-local venv is required."
	@echo "PYTHONPATH=src python -m qual_lab.main --version"
	PYTHONPATH=src python -m qual_lab.main --version

lint:
	python -m ruff check .

typecheck:
	python -m mypy src

test:
	python -m pytest -q

release-check:
	PYTHONPATH=src python -m qual_lab.main doctor
	python -m ruff check .
	python -m mypy src
	python -m pytest -q

check:
	python -m ruff check .
	python -m mypy src
	python -m pytest -q
