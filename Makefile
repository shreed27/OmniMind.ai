VENV := $(shell pwd)/.venv

.PHONY: bootstrap lint test typecheck security clean

bootstrap:
	python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip
	$(VENV)/bin/pip install -r backend/requirements-dev.txt
	cd frontend && npm install

lint:
	cd backend && $(VENV)/bin/python -m ruff check .
	cd backend && $(VENV)/bin/python -m mypy .
	cd frontend && npm run lint

typecheck:
	cd backend && $(VENV)/bin/python -m mypy .
	cd frontend && npm run typecheck

test:
	$(VENV)/bin/python -m pytest backend/tests -q
	cd frontend && npm test -- --run

security:
	cd backend && pip-audit || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
