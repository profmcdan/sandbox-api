import logging
from urllib.parse import urlparse

import redis
from django.conf import settings
from django.db import OperationalError, connections
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
def readiness_check(request):
    response = {"database": "unknown", "redis": "unknown"}

    # Check database connection
    try:
        db_conn = connections["default"]
        db_conn.cursor()
        response["database"] = "ready"
    except OperationalError:
        response["database"] = "not ready"

    # Check Redis connection
    try:
        redis_url = urlparse(settings.REDIS_URL)
        r = redis.StrictRedis(
            host=redis_url.hostname,
            port=redis_url.port,
            password=redis_url.password,
            decode_responses=True,
        )
        r.ping()
        response["redis"] = "ready"
    except redis.ConnectionError:
        response["redis"] = "not ready"

    return Response(response)


@api_view(["GET"])
def health_check(request):
    def get_client_ip(request):
        ip_addresses = [
            request.META.get("REMOTE_ADDR", ""),
            request.META.get("HTTP_X_FORWARDED_FOR", ""),
        ]
        return [addr for addr in ip_addresses if addr]

    remote_addresses = get_client_ip(request)
    logger.info({"remote_addresses": remote_addresses})

    response = {"status": True}
    return Response(response)
