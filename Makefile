ARG ?= maps/easy/01_linear_path.txt

PY3 = python3

PIP = pip

NAME = fly_in.py

FLAKE = flake8

EXCLUDE_DIR = --exclude=.venv,venv,env

MYPY = mypy

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

DEBUG = pdb

CACHE = .mypy_cache 

install:
	$(PIP) install -r requirements.txt

uninstall:
	$(PIP) uninstall -r requirements.txt

run:
	$(PY3) $(NAME) $(ARG)

debug:
	$(PY3) -m $(DEBUG) $(NAME) $(ARG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(CACHE)

lint:
	$(FLAKE) . $(EXCLUDE_DIR); $(MYPY) . $(MYPY_FLAGS) $(EXCLUDE_DIR)

lint-strict:
	$(FLAKE) . $(EXCLUDE_DIR); $(MYPY) . --strict $(EXCLUDE_DIR)

.PHONY: install run debug clean lint lint-strict
