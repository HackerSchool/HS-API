FROM python:3.11-slim

WORKDIR /hs-api
RUN python -m pip install --upgrade pip
RUN pip install uv
COPY . .
EXPOSE 5000

CMD ["uv", "run", "gunicorn", "-c", "gunicorn_conf.py", "app:create_app()"]