setup-all: setup setup-dev

setup: setup-pipenv setup-commands build_ext

setup-dev: setup-pipenv setup-dev-commands

clean: clean-venv clean-setuppy clean-cython

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

clean-cython:
	rm -rf ton_client/ton_clib/*.c
	rm -rf ton_client/ton_clib.*.so

bdist-wheel: setup-dev
	pipenv run python setup.py bdist_wheel

build_ext: setup-dev
	pipenv run python setup.py build_ext --inplace