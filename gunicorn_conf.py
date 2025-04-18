# gunicorn_config.py
bind = "0.0.0.0:5000"
accesslog = "/hs-api/data/logs/access.log"
errorlog = "/hs-api/data/logs/error.log"
loglevel = "info"
access_log_format = (
    '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)
