SHELL = /bin/sh

default:

.PHONY: run
run:
	pipenv run python run.py

.PHONY: deps-install
deps-install:
	pipenv install --dev

.PHONY: deps-update
deps-update:
	pipenv update --dev

.PHONY: black-check
black-check:
	pipenv run black --check .

.PHONY: test
test:
	pipenv run pytest --cov bot --verbose tests
