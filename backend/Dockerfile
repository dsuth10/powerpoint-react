# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install Python dependencies first for caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Dev-only dependencies in a separate stage
FROM base AS devdeps
COPY backend/requirements-dev.txt ./requirements-dev.txt
RUN pip install -r requirements-dev.txt

# Copy app code
COPY backend/app ./app
COPY backend/pytest.ini ./pytest.ini
COPY backend/.flake8 ./.flake8

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]