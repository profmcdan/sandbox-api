# middleware/opensearch_logger.py

import json
import traceback
from datetime import datetime

from common.audtilog.contrib import mask_sensitive_data
from custom_logger.tasks import send_log_to_opensearch
import logging

logger = logging.getLogger(__name__)

class OpenSearchLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = datetime.utcnow()

        try:
            response = self.get_response(request)

            duration = (
                datetime.utcnow() - start_time
            ).total_seconds() * 1000

            request_body = None
            response_body = None

            # Request body
            try:
                if request.body:
                    request_body = request.body.decode("utf-8")
            except Exception:
                request_body = "Unable to decode body"

            # Response body
            try:
                if hasattr(response, "content"):
                    response_body = response.content.decode("utf-8")

                    # Pretty print JSON responses
                    try:
                        response_body = json.dumps(
                            json.loads(response_body),
                            indent=2,
                        )
                    except Exception:
                        pass

            except Exception:
                response_body = "Unable to decode response body"

            log_data = {
                "level": "INFO",
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "ip_address": self.get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
                "response_time_ms": duration,
                "request_body": mask_sensitive_data(request_body),
                "response_body": mask_sensitive_data(response_body),
            }
            # Send asynchronously to Celery
            send_log_to_opensearch.delay(log_data)

            return response

        except Exception as exc:
            error_log = {
                "level": "ERROR",
                "method": request.method,
                "path": request.path,
                "ip_address": self.get_client_ip(request),
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }

            send_log_to_opensearch.delay(error_log)

            raise exc

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]

        return request.META.get("REMOTE_ADDR")
