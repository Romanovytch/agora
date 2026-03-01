SHELL := /bin/bash

.PHONY: help venv install run test lint format format-check ci

help:
	@echo "Targets:"
	@echo "  make venv          - Create venv (.venv)"
	@echo "  make install       - Install AgoRa (editable) + dev tools"
	@echo "  make test          - Run tests (pytest)"
	@echo "  make lint          - Run ruff lint (check)"
	@echo "  make format        - Auto-format with ruff"
	@echo "  make format-check  - Check formatting with ruff"
	@echo "  make ci            - Run lint + format-check + tests"

venv:
	python -m venv .venv

install:
	. .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && ruff format . && ruff check . --fix

format-check:
	. .venv/bin/activate && ruff format --check .

ci: lint format-check test