#! /bin/sh

flask db upgrade

exec "$@"