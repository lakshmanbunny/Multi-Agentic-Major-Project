FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.6.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./
COPY libs/core ./libs/core

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with ml_worker

# Copy service code
COPY services/ml_worker ./services/ml_worker

# Expose port
EXPOSE 8002

# Run the service
CMD ["uvicorn", "services.ml_worker.main:app", "--host", "0.0.0.0", "--port", "8002"]
