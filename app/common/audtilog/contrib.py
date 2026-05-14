import logging
import re

import jwt
from django.conf import settings
from ipware import get_client_ip as ipware_get_client_ip

logger = logging.getLogger(__name__)


SENSITIVE_KEYS = [
    "password",
    "token",
    "access",
    "refresh",
    "Authorization",
    "pin",
    "tx_pin",
]

logger = logging.getLogger(__name__)
# settings.configure()

if hasattr(settings, "API_LOGGER_EXCLUDE_KEYS"):
    if type(settings.DRF_API_LOGGER_EXCLUDE_KEYS) in (list, tuple):
        SENSITIVE_KEYS.extend(settings.DRF_API_LOGGER_EXCLUDE_KEYS)


def get_headers(request=None):
    """
    Function:       get_headers(self, request)
    Description:    To get all the headers from request
    """
    regex = re.compile("^HTTP_")
    return dict(
        (regex.sub("", header), value)
        for (header, value) in request.META.items()
        if header.startswith("HTTP_")
    )


def get_client_ip(request) -> str:
    """
    Retrieve the real client IP using django-ipware.
    Handles proxies (Nginx, AWS ELB, etc.) via proxy_count or header order.
    """
    try:
        # proxy_count=1 means Django is behind 1 proxy (e.g. Nginx or AWS ALB).
        client_ip, is_routable = ipware_get_client_ip(
            request,
            proxy_count=1,  # adjust to your infra (0 if no proxy, 1 for nginx/ALB, etc.)
            request_header_order=[
                "X_FORWARDED_FOR",
                "HTTP_X_FORWARDED_FOR",
                "HTTP_X_REAL_IP",
                "HTTP_CLIENT_IP",
            ],
        )

        if client_ip is None:
            # Fallback: try reading directly from META
            client_ip = request.META.get("REMOTE_ADDR", "")
            logger.warning(
                f"ipware returned None — falling back to REMOTE_ADDR: {client_ip}"
            )

        if not is_routable:
            logger.info(
                f"IP {client_ip} is private/loopback — geo lookup will return None"
            )

        logger.info(f"Resolved client IP: {client_ip} | routable: {is_routable}")
        return client_ip or ""

    except Exception as ex:
        logger.error(f"Error resolving client IP: {ex}")
        return ""


# def get_client_ip(request):
#     try:
#         x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#         if x_forwarded_for:
#             ip = x_forwarded_for.split(",")[0]
#         else:
#             ip = request.META.get("REMOTE_ADDR")
#         return ip
#     except Exception as ex:
#         logger.error(ex)
#         return ""


def mask_sensitive_data(data, mask_api_parameters=True):
    mask_value = "***FILTERED***"
    # Check if data is a dictionary
    if isinstance(data, dict):
        # Create a copy of the dictionary to avoid modifying the original
        masked_data = {}
        for key, value in data.items():
            # If the key is in sensitive fields, mask the value
            if key in SENSITIVE_KEYS:
                masked_data[key] = mask_value
            else:
                # Recursively process nested structures
                masked_data[key] = mask_sensitive_data(value, mask_api_parameters)
        return masked_data

    # If data is a list, apply the function to each item in the list
    elif isinstance(data, list):
        return [mask_sensitive_data(item, mask_api_parameters) for item in data]

    # For other data types, return the data as is
    else:
        return data


def mask_sensitive_data_v1(data, mask_api_parameters=True):
    """
    Hides sensitive keys specified in sensitive_keys settings.
    Loops recursively over nested dictionaries.
    When the mask_api_parameters parameter is set, the function will
    instead iterate over sensitive_keys and remove them from an api
    URL string.
    """
    if not isinstance(data, dict):
        # Handle strings with masking sensitive keys in API parameters
        if mask_api_parameters and isinstance(data, str):
            for sensitive_key in SENSITIVE_KEYS:
                data = re.sub(
                    rf"({sensitive_key}=)(.*?)($|&)",  # Use raw strings for clarity
                    r"\1***FILTERED***\3",
                    data,
                )
        # Handle lists by recursively masking sensitive data in each item
        elif isinstance(data, list):
            data = [mask_sensitive_data(item) for item in data]

        return data

    for key, value in data.items():
        if key in SENSITIVE_KEYS:
            data[key] = "***FILTERED***"

        if type(value) is dict:
            data[key] = mask_sensitive_data(data[key])

        if type(value) is list:
            data[key] = [mask_sensitive_data(item) for item in data[key]]

    return data


def decode_jwt_token(request):
    authorization_header = request.headers.get("Authorization", "")
    if authorization_header.startswith("Bearer "):
        token = authorization_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = decoded_token.get("email")
            user_id = decoded_token.get("user_id")
            fullname = decoded_token.get("fullname")
            return email, user_id, fullname
        except jwt.DecodeError:
            # Handle decoding error (e.g., log it, return default values)
            return "", "", ""
    else:
        return "", "", ""
