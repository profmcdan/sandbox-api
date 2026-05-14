from datetime import datetime

from core.celery import APP
from django.conf import settings

from .mongo_connector import get_database
from .opensearch import opensearch_client, INDEX_NAME

database = get_database()
app_name = settings.APP_NAME.lower()
db_name = settings.MONGODB_LOGGER_DATABASE
collection_name = database[db_name]


@APP.task()
def send_logs_to_logger(data):
    inserted_id = collection_name.insert_one(data).inserted_id
    # elastic_search = Elasticsearch(hosts=settings.MONGODB_LOGGER_URL)
    # result = elastic_search.index(index=settings.APP_NAME.lower(), body=data)
    return {
        "entry": str(inserted_id),
        "app_name": app_name,
        "db_name": db_name,
        "timestamp": str(datetime.now()),
    }


@APP.task()
def send_log_to_auditlogger(data):
    pass


@APP.task()
def send_logs_to_opensearch_logger(data):
    try:
        # Add timestamp if missing
        data["@timestamp"] = datetime.now().isoformat()

        response = opensearch_client.index(
            index=INDEX_NAME,
            body=data,
            refresh=False,
        )

        return {
            "entry": response["_id"],
            "index": response["_index"],
            "app_name": app_name,
            "timestamp": str(datetime.now()),
            "status": "success",
        }

    except Exception as exc:
        return {
            "status": "failed",
            "error": str(exc),
            "app_name": app_name,
            "timestamp": str(datetime.now()),
        }
