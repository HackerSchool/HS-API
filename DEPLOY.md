## Deployment

You can simply edit the `.env` configuration and use `docker compose`.
This runs the backend container alongside a redis session backend so these options should be enabled in the configuration. 

**Note**: You need to prepare the DB before launching the containers. 

```bash
python -m pip install --upgrade pip
pip install uv
uv sync
uv run flask run db upgrade
```

Create your admin user if necessary:
```bash
uv run flask create-admin myusername mypassword ist1xxxxxx
```

If you want to setup your own reverse proxy you can remove the caddy container from `docker-compose.yaml`. With caddy it will
automatically generate a TLS certificate if the domain present in the Caddyfile (currently `api.hackerschool.dev`) is correctly 
pointing to the machine hosting these containers. 

---

Useful commands to inspect the deployed containers:

Launch a sqlite3 shell on the backend database:
```sh
docker run --rm -it -v ./resources:/data nouchka/sqlite3 /data/hackerschool.sqlite3
```

Launch a redis shell on the session backend:
```sh
docker run -it --network <hs-bridge-network> --rm redis redis-cli -h <hs-redis-container>
```
