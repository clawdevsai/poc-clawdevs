PYTHON ?= python

.PHONY: help test clean

help:
	@echo "make test   - executa a suite"
	@echo "make clean  - remove caches Python"

test:
	@$(PYTHON) -m pytest -q

clean:
	@cmd /c "for /d /r %d in (__pycache__) do @if exist \"%d\" rd /s /q \"%d\"" || true
	@cmd /c "if exist .pytest_cache rd /s /q .pytest_cache" || true
