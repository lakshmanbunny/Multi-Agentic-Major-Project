FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.6.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./
COPY libs/core ./libs/core

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with orchestrator

# Copy service code
COPY services/orchestrator ./services/orchestrator

# Expose port
EXPOSE 8000

# Run the service
CMD ["uvicorn", "services.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
