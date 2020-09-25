setup-all: setup setup-dev

setup: setup-poetry setup-commands

setup-dev: setup-poetry setup-dev-commands

setup-env: setup-env38

build: build-wheel

test: test-flake8 test-pytest

clean: clean-venv clean-build clean-pytest clean-tonlib

setup-poetry:
ifeq (, $(shell which pipenv))
	pip3 install --pre poetry
endif

setup-env38:
	# might be incompatible in arbitrary environment
	poetry env use python3.8

setup-dev-commands:
	$(make) poetry install

setup-commands:
	$(make) poetry install --no-dev

test-flake8:
	poetry run flake8 ton_client testsuite

test-pytest:
	poetry run pytest

activate:
	poetry shell

clean-venv:
	rm -rf .venv

clean-build:
	rm -rf dist

clean-pytest:
	rm -rf .pytest_cache

clean-tonlib:
	find ./* -name *.blkstate | xargs rm -rf

build-wheel: setup-dev
	poetry build