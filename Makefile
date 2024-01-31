run:
	# Executes the given command inside the virtualenv
	poetry run gptauthor --story openai-drama --total-chapters 3 --llm-model gpt-3.5-turbo --llm-temperature 0.1 --llm-top-p 1.0

run-no-allow-user-input:
	# Executes the given command inside the virtualenv
	poetry run gptauthor --story openai-drama --total-chapters 3 --llm-model gpt-3.5-turbo --llm-temperature 0.1 --llm-top-p 1.0 --no-allow-user-input

build:
	# Build the source and wheels archives
	poetry build

install:
	# Read pyproject.toml, resolves the dependencies, and installs them.
	poetry install

publish:
	# One time: poetry config pypi-token.pypi <your-pypi-token>
	# Publishes the package to the remote repository
	poetry publish --build

which-python:
	poetry run which python

poetry-add-init:
	# Adds required packages to your pyproject.toml and installs them
	# TODO: review and add your dependencies as needed
	poetry add --group dev pytest black ruff coverage pre-commit pip-audit
	poetry add python-dotenv click typer rich tqdm loguru

publish-test:
	# One time: poetry config repositories.test-pypi https://test.pypi.org/legacy/
	# One time: poetry config pypi-token.test-pypi <your-test-pypi-token>
	poetry publish -r test-pypi

test-install-from-pypi:
	rm -rf venv_install_test
	python3 -m venv venv_install_test
	source venv_install_test/bin/activate ; pip install gptauthor
	source venv_install_test/bin/activate ; gptauthor --help
	source venv_install_test/bin/activate ; gptauthor --version
	source venv_install_test/bin/activate ; pip list | grep gptauthor
	rm -rf venv_install_test

poetry-config:
	poetry config --list

poetry-show-tree:
	poetry show --tree

poetry-gen-requirements:
	poetry export --output requirements.txt

test:
	poetry run coverage run -m pytest -vvv -s ./tests
	poetry run coverage report

test-selected:
	poetry run coverage run -m pytest -vvv -s ./tests -k test_console
	poetry run coverage report

black-check:
	poetry run black gptauthor tests --check --verbose

black:
	poetry run black gptauthor tests

ruff-check:
	poetry run ruff check .

ruff:
	poetry run ruff check . --fix

pre-commit:
	poetry run pre-commit run --all-files

pip-audit:
	poetry run pip-audit

.DEFAULT_GOAL := help
.PHONY: help
help:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
