MAIN        := src/main.py
MAP         ?= maps/easy1.txt

install:
	@pip install -r requirements.txt

run:
	@python3 $(MAIN) $(MAP)

debug:
	@python3 -m pdb $(MAIN) $(MAP)

lint:
	@flake8 .
	@mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@find . -type f -name "*.pyc" -delete

.PHONY: install run debug lint lint-strict clean