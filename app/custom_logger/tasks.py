# logging/tasks.py

import socket
from datetime import datetime

from celery import shared_task
from django.conf import settings
from opensearchpy import OpenSearch


client = OpenSearch(
    hosts=[
        {
            "host": settings.OPENSEARCH_HOST,
            "port": settings.OPENSEARCH_PORT,
        }
    ],
    http_auth=(
        settings.OPENSEARCH_USERNAME,
        settings.OPENSEARCH_PASSWORD,
    ),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    http_compress=True,
    timeout=5,
    max_retries=2,
    retry_on_timeout=True,
    pool_maxsize=20,
    refresh=False,
)

INDEX_NAME = getattr(
    settings,
    "OPENSEARCH_INDEX",
    settings.APP_NAME.lower(),
)


def ensure_index_exists():
    if not client.indices.exists(index=INDEX_NAME):
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "method": {"type": "keyword"},
                    "path": {"type": "text"},
                    "status_code": {"type": "integer"},
                    "ip_address": {"type": "ip"},
                    "user_agent": {"type": "text"},
                    "response_time_ms": {"type": "float"},
                    "request_body": {"type": "text"},
                    "response_body": {"type": "text"},
                    "hostname": {"type": "keyword"},
                    "error": {"type": "text"},
                    "traceback": {"type": "text"},
                }
            },
        }

        client.indices.create(
            index=INDEX_NAME,
            body=mapping,
        )


@shared_task(bind=True, max_retries=3)
def send_log_to_opensearch(self, log_data):
    ensure_index_exists()

    log_data["@timestamp"] = datetime.utcnow().isoformat()
    log_data["hostname"] = socket.gethostname()

    response = client.index(
        index=INDEX_NAME,
        body=log_data,
    )

    return response["_id"]
