FROM python:3.11-slim

WORKDIR /app
COPY requirements-prod.txt .
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.api:entry"]