setup-all: setup setup-dev

setup: setup-pipenv setup-commands

setup-dev: setup-pipenv setup-dev-commands

clean: clean-venv clean-setuppy clean-tonlib

setup-pipenv:
ifeq (, $(shell which pipenv))
	pip install pipenv
endif

setup-dev-commands:
	PIPENV_VENV_IN_PROJECT=1 PIPENV_IGNORE_VIRTUALENVS=1 $(make) pipenv install --dev

setup-commands:
	PIPENV_VENV_IN_PROJECT=1 PIPENV_IGNORE_VIRTUALENVS=1 $(make) pipenv install

activate:
	pipenv shell

clean-venv:
	rm -rf .venv

clean-setuppy:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

clean-tonlib:
	find ./* -name *.blkstate | xargs rm -rf

bdist-wheel: setup-dev
	pipenv run python setup.py bdist_wheel
