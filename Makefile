FLAKE8 = flake8
MYPY = mypy
FLAGS = --warn-return-any --warn-unused-ignores \
--ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs

.PHONY = install, run, test, debug, clean, lint, lint-strict

install:
	uv add -r pyproject.toml

run:
	uv run python3 -m src

test:
	uv run python3 -m src --test

debug:
	uv run python3 --debug -m src

clean:
	echo "a"

lint:
	$(FLAKE8) src
	$(MYPY) $(FLAGS) src

lint-strict:
	$(FLAKE8) src
	$(MYPY) --strict src
