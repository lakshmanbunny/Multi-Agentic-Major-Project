FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.6.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./
COPY libs/core ./libs/core

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with browser_agent

# Install Playwright browsers
RUN poetry run playwright install --with-deps chromium

# Copy service code
COPY services/browser_agent ./services/browser_agent

# Expose port
EXPOSE 8001

# Run the service
CMD ["uvicorn", "services.browser_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
