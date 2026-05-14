import datetime
import json
import logging

from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin

# Get the logger instance
logger = logging.getLogger(__name__)


class RequestResponseLoggerMiddleware(MiddlewareMixin):
    """
    Middleware to log requests and responses to the console.
    """

    def process_request(self, request):
        # Save the raw body for later use
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            try:
                request.raw_body_data = request.body
            except Exception as e:
                logger.error(f"Failed to read request body: {e}")
                request.raw_body_data = None

        # Add start time for logging request duration
        request.start_time = datetime.datetime.now()

    def process_response(self, request, response):
        # Calculate duration
        start_time = getattr(request, "start_time", datetime.datetime.now())
        duration = datetime.datetime.now() - start_time

        # Resolve URL name and namespace
        try:
            resolver_match = resolve(request.path_info)
            # url_name = resolver_match.url_name
            namespace = resolver_match.namespace
        except Resolver404:
            # url_name = None
            namespace = None

        # Parse request body safely
        request_data = {}
        raw_body = getattr(request, "raw_body_data", b"")
        if request.content_type == "application/json" and raw_body:
            try:
                request_data = json.loads(raw_body)
            except json.JSONDecodeError:
                request_data = raw_body.decode("utf-8", errors="replace")
        elif request.content_type in [
            "multipart/form-data",
            "application/x-www-form-urlencoded",
        ]:
            if hasattr(request, "POST"):
                request_data = request.POST.dict()
            if hasattr(request, "FILES") and request.FILES:
                request_data["files"] = {
                    key: file.name for key, file in request.FILES.items()
                }

        # Log only non-admin and relevant HTTP methods
        if namespace != "admin" and request.method in [
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            try:
                response_content = (
                    json.loads(response.content.decode("utf-8"))
                    if response.content
                    else None
                )
            except (json.JSONDecodeError, AttributeError):
                response_content = (
                    response.content.decode("utf-8", errors="replace")
                    if response.content
                    else None
                )

            logger.info(
                {
                    "request": {
                        "path": request.path,
                        "method": request.method,
                        "body": request_data,
                    },
                    "response": {
                        "status_code": response.status_code,
                        "content": response_content,
                    },
                    "duration": duration.total_seconds(),
                }
            )

        return response
