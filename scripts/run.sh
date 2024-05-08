#!/bin/sh

# faz o script parar de rodar se der erro em qualquer linha
set -e

# espera o db ficar pronto
python manage.py wait_for_db
python manage.py collectstatic --noinput
# run any migrations in case of db changes
python manage.py migrate
# run uWSGI service
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi