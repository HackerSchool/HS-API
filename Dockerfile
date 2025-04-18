FROM python:3.11-slim

WORKDIR /hs-api
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
COPY . .
EXPOSE 5000
RUN chmod u+x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
CMD ["gunicorn", "-c", "gunicorn_conf.py", "app:create_app()"]