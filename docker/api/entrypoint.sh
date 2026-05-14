#!/bin/sh

#python manage.py  migrate --no-input
#python manage.py migrate --database=audit_db --no-input
# python manage.py seed_currency
#rm celerybeat.pid

exec "$@"
