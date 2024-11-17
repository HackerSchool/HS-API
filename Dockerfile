FROM python:3.11-slim

WORKDIR /hs-api
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
COPY . .
EXPOSE 8000
RUN chmod u+x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()", "--log-level", "info", "--access-logfile", "/hs-api/data/logs/access.log", "--error-logfile", "/hs-api/data/logs/error.log"]