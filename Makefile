.PHONY: bootstrap lint test typecheck security clean

bootstrap:
	python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

lint:
	cd backend && ruff check .
	cd backend && mypy .
	cd frontend && npm run lint

typecheck:
	cd backend && mypy .
	cd frontend && npm run typecheck

test:
	cd backend && .venv/bin/python -m pytest -q
	cd frontend && npm test -- --run

security:
	cd backend && pip-audit || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
