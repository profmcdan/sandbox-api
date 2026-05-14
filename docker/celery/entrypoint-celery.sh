#!/bin/sh

set -ex

# Start Celery worker
#celery -A core worker --loglevel=info --autoscale=6,2 --max-tasks-per-child=100 --hostname=worker@%h --detach

# celery -A core worker --loglevel=info --max-tasks-per-child=200 --autoscale=6,2 --hostname=worker1@%h --detach
# celery -A core worker --loglevel=info --max-tasks-per-child=200 --autoscale=6,2 --hostname=worker2@%h --detach
# celery -A core worker --loglevel=info --max-tasks-per-child=200 --autoscale=6,2 --hostname=worker3@%h --detach
# celery -A core worker --loglevel=info --max-tasks-per-child=200 --autoscale=6,2 --hostname=worker4@%h --detach

# celery -A core worker \
#   --loglevel=info --queues=logger_queue \
#   --autoscale=6,2 --hostname=logger_worker@%h \
#   --prefetch-multiplier=1 --max-tasks-per-child=200 --detach

# celery -A core worker \
#   --loglevel=info --queues=report_queue \
#   --autoscale=6,2 --hostname=report_worker@%h \
#   --prefetch-multiplier=1 --max-tasks-per-child=200 --detach

# celery -A core worker \
#   --loglevel=info --queues=comms_queue \
#   --autoscale=6,2 --hostname=comms_worker@%h \
#   --prefetch-multiplier=1 --max-tasks-per-child=200 --detach


# #celery -A core beat -l debug --detach
# celery -A core beat -l info --detach --scheduler django_celery_beat.schedulers:DatabaseScheduler

exec "$@"
