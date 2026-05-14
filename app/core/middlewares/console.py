import datetime
import json
import logging

from common.audtilog.contrib import get_headers, mask_sensitive_data
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin
from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse
from ipware import get_client_ip
from sentry_sdk import capture_exception

# Get the logger instance
logger = logging.getLogger(__name__)


class CaptureExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if exception:
            capture_exception(exception)
            return JsonResponse(
                {
                    "type": "server_error",
                    "errors": [
                        {
                            "code": "server_side_error",
                            "detail": "An Error Occurred. Please try again",
                            "attr": "detail",
                        }
                    ],
                },
                status=500,
            )


class ValidationErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response: HttpResponse = self.get_response(request)

        content_type = response.headers.get("Content-Type")
        if (
            content_type
            and content_type == "application/json"
            and response.status_code == 400
        ):
            data = json.loads(response.content)
            if (
                isinstance(data, dict)
                and not data.get("detail")
                and not data.get("errors")
            ):
                data = {"success": False, "errors": data}
            response.content = json.dumps(data)

        return response


class DrfExceptionFormatter(ExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        error = error_response.errors[0]
        return {
            "type": error_response.type,
            "code": error.code,
            "message": error.detail,
            "field_name": error.attr,
        }


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    @staticmethod
    def get_custom_response(response):
        if response.get("content-type") == "application/gzip":
            response_body = "** GZIP Archive **"
        elif response.get("content-type") == "application/octet-stream":
            response_body = "** Binary File **"
        elif getattr(response, "streaming", False):
            response_body = "** Streaming **"
        else:
            if isinstance(response.content, bytes):
                response_body = json.loads(response.content.decode())
            else:
                response_body = json.loads(response.content)

        return response_body

    # def process_request(self, request):
    #     # Log incoming request details
    #     logger.info(f"Request - Method: {request.method}, Path: {request.path}, Body: {request.body}")

    def process_response(self, request, response):
        logger.info(
            f"Request - Method: {request.method}, Path: {request.path}, Body: {request.body}"
        )
        # Log response details
        logger.info(f"Response - Status Code: {response.status_code}")
        return response


class RequestResponseLoggerMiddleware:
    """
    Middleware to log requests and responses to the console.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        start_time = datetime.datetime.now()
        body = request.body  # this reads it once
        request._body = body  # reassign it back so Django/DRF can still parse it

        # Process the request
        response = self.get_response(request)

        # Log response details
        duration = datetime.datetime.now() - start_time
        try:
            resolver_match = resolve(request.path_info)
            # url_name = resolver_match.url_name
            namespace = resolver_match.namespace
        except Resolver404:
            # resolver_match = None
            # url_name = None
            namespace = None

        request_data = {}
        if request.content_type == "application/json":
            try:
                if request.path in getattr(settings, "ENCRYPTED_ROUTE", []):
                    request_data = request.decrypted_payload
                else:
                    request_data = json.loads(body.decode("utf-8")) if body else {}
            except json.JSONDecodeError:
                request_data = request.body.decode("utf-8")
        elif request.content_type in [
            "multipart/form-data",
            "application/x-www-form-urlencoded",
        ]:
            request_data = request.POST.dict()
            if request.FILES:
                request_data["files"] = {
                    key: file.name for key, file in request.FILES.items()
                }

        if namespace != "admin" and request.method in [
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            try:
                response_data = (
                    json.loads(response.content.decode("utf-8"))
                    if response.content
                    else None
                )
            except Exception as e:
                logger.error(e)
                response_data = {}
            if isinstance(request_data, dict):
                request_data.pop("payment_instruction", None)

            headers = json.dumps(
                mask_sensitive_data(get_headers(request), mask_api_parameters=True),
                indent=4,
                ensure_ascii=False,
            )
            client_ip, routable = get_client_ip(request)
            data = dict(
                app_name="wallet-api",
                api=request.path,
                headers=headers,
                body=mask_sensitive_data(request_data),
                method=request.method,
                client_ip_address=client_ip,
                response=mask_sensitive_data(response_data, mask_api_parameters=True),
                status_code=response.status_code,
                execution_time=duration.total_seconds(),
                added_on=str(datetime.datetime.now()),
                environment=settings.ENVIRONMENT_INSTANCE,
                device=request.META.get("HTTP_USER_AGENT", "unknown"),
                source="phoenix-wallet-api-request",
            )

            logger.info(data)
        return response
