SHELL = /bin/sh

default:

.PHONY: run
run:
	pipenv run python main.py

.PHONY: deps-install
deps-install:
	pipenv install --dev --pre

.PHONY: deps-update
deps-update:
	pipenv update --dev --pre

.PHONY: black-check
black-check:
	pipenv run black --check .

.PHONY: pyflakes-check
pyflakes-check:
	pipenv run pyflakes .

.PHONY: check
check: black-check pyflakes-check

.PHONY: test
test:
	pipenv run pytest --verbose --cov sovyak --cov-report term-missing
