FROM python:3.11-slim

WORKDIR /hs-api

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pip and uv
RUN python -m pip install --upgrade pip
RUN pip install uv

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create resources directory if it doesn't exist
RUN mkdir -p resources/flask_sessions resources/images

# Expose port (internal port 5000, mapped to 8080 externally)
EXPOSE 5000

# Run gunicorn
CMD ["uv", "run", "gunicorn", "-c", "gunicorn_conf.py", "app:create_app()"]