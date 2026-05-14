#!/bin/sh
set -ex

celery -A core worker \
  --loglevel=info --queues=migration_queue \
  --concurrency=1 --hostname=migration_worker@%h \
  --prefetch-multiplier=1 --max-tasks-per-child=100 &
PID5=$!

celery -A core worker \
  --loglevel=info --queues=logger_queue \
  --concurrency=1 --hostname=logger_worker@%h \
  --prefetch-multiplier=1 --max-tasks-per-child=100 &
PID6=$!

celery -A core worker \
   --loglevel=info --queues=comms_queue \
   --concurrency=2 --hostname=comms_worker@%h \
   --max-tasks-per-child=100 &
PID7=$!

#celery -A core worker --loglevel=info --queues=kams_migration_queue --concurrency=1 --hostname=migration_worker@%h --prefetch-multiplier=1 --detach

# Start Celery beat
celery -A core beat \
  -l info \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler &
PID8=$!

# Keep the container running
wait $PID5 $PID6 $PID7 $PID8
