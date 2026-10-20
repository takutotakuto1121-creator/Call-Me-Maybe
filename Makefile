FLAKE8 = flake8
MYPY = mypy
FLAGS = --warn-return-any --warn-unused-ignores \
--ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs

.PHONY = install run test debug clean lint lint-strict

install:
	uv pip install -r .

run:
	uv run python3 -m src

animation:
	uv run python3 -m src --animation 1

test:
	uv run python3 -m src --test 1 --animation 1

debug:
	uv run python3 -pdb -m src

clean:
	rm -rf */__pycache__/
	rm -rf .vscode/
	rm -rf .python-version
	rm -rf .mypy_cache/

fclean: clean
	rm -rf .venv/
	rm -rf data/output/

lint:
	$(FLAKE8) src
	$(MYPY) $(FLAGS) src

lint-strict:
	$(FLAKE8) src
	$(MYPY) --strict src
