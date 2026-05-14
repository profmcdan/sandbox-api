from drf_standardized_errors.handler import (
    exception_handler as standardized_exception_handler,
)
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

TARGET_PATHS = [
    "/api/v1/payments/",
    "/api/v1/payment/",
]


def custom_exception_handler(exc, context):
    request = context.get("request")

    # Route to the right handler based on path
    if request and any(request.path.startswith(path) for path in TARGET_PATHS):
        return _payment_exception_handler(exc, context)
    else:
        return standardized_exception_handler(exc, context)


def _payment_exception_handler(exc, context):
    response = exception_handler(exc, context)
    response_code = None

    if response is None:
        return response

    # Extract real error message
    if isinstance(response.data, dict):
        if "detail" in response.data:
            message = response.data["detail"]
        elif "message" in response.data:
            message = response.data["message"]
        else:
            message = "; ".join(
                f"{key}: {', '.join(value) if isinstance(value, list) else value}"
                for key, value in response.data.items()
            )
    else:
        message = str(response.data)

    # Default response code
    response_code = "07"

    # Allow custom exceptions to define their own response code
    if isinstance(exc, APIException) and hasattr(exc, "response_code"):
        response_code = exc.response_code

    response.data = {
        "success": False,
        "requestSuccessful": False,
        "responseCode": response_code,
        "responseMessage": message,
        "responseBody": {},
        "statusCode": str(response.status_code),
    }

    return response
