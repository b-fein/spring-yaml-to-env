# SPDX-FileCopyrightText: 2022 Benedikt Fein
#
# SPDX-License-Identifier: EUPL-1.2

PROJECT=spring_yaml_to_env

.PHONY: test
test:
	poetry run pytest --cov=$(PROJECT) --cov=tests --cov-branch --junitxml=report.xml --cov-report=term-missing --cov-report html:cov_html tests/

.PHONY: format
format:
	poetry run isort .
	poetry run ruff format .

.PHONY: mypy
mypy:
	poetry run mypy $(PROJECT) tests

.PHONY: ruff
ruff:
	poetry run ruff check $(PROJECT) tests

.PHONY: darglint
darglint:
	poetry run darglint2 -s sphinx -v 2 $(PROJECT)/*.py

.PHONY: reuse
reuse:
	poetry run reuse lint

.PHONY: check
check: format mypy ruff darglint reuse
