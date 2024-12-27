# SPDX-FileCopyrightText: 2022 Benedikt Fein
#
# SPDX-License-Identifier: EUPL-1.2

PROJECT=src

.PHONY: test
test:
	uv run pytest --cov=$(PROJECT) --cov=tests --cov-branch --junitxml=report.xml --cov-report=term-missing --cov-report html:cov_html tests/

.PHONY: format
format:
	uv run isort $(PROJECT) tests
	uv run ruff format $(PROJECT) tests

.PHONY: mypy
mypy:
	uv run mypy $(PROJECT) tests

.PHONY: ruff
ruff:
	uv run ruff check $(PROJECT) tests

.PHONY: darglint
darglint:
	uv run darglint2 -s sphinx -v 2 $(PROJECT)/**/*.py

.PHONY: reuse
reuse:
	uv run reuse lint

.PHONY: check
check: format mypy ruff darglint reuse
