FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY backend/pyproject.toml backend/requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt && \
    pip install -e .

COPY backend/app ./app
COPY kernel ./kernel

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
