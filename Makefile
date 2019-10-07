SHELL = /bin/sh

default:

.PHONY: run
run:
	pipenv run python run.py

.PHONY: deps/install
deps/install:
	pipenv install --dev --pre

.PHONY: deps/update
deps/update:
	pipenv update --dev --pre

.PHONY: black/check
black/check:
	pipenv run black --check .

.PHONY: test
test:
	pipenv run pytest --cov sovyak --verbose tests
