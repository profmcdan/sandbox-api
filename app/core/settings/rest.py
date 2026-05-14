import os
from datetime import timedelta

APP_DESCRIPTION = os.environ.get("APP_DESCRIPTION", "Phlox Wallet API")

# DATE_INPUT_FORMATS = [
#     "%d/%m/%Y",
#     "%d/%m/%y",  # '10/02/2020', '10/02/20'
#     "%Y-%m-%d",
#     "%m/%d/%Y",
#     "%m/%d/%y",  # '2006-10-25', '10/25/2006', '10/25/06'
#     "%b %d %Y",
#     "%b %d, %Y",  # 'Oct 25 2006', 'Oct 25, 2006'
#     "%d %b %Y",
#     "%d %b, %Y",  # '25 Oct 2006', '25 Oct, 2006'
#     "%B %d %Y",
#     "%B %d, %Y",  # 'October 25, 2006', 'October 25, 2006'
#     "%d %B %Y",
#     "%d %B, %Y",  # '25 October 2006', '25 October 2006'
# ]


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    # 'DATE_INPUT_FORMATS': ["%d/%m/%Y", ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "pykolofinance.authentication.CustomJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "EXCEPTION_HANDLER": "common.custom_exception_handler.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATE_FORMAT": "%Y-%m-%d",
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
}

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "DEFAULT_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_PATCH": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "displayRequestDuration": True,
    },
    "UPLOADED_FILES_USE_URL": True,
    "TITLE": APP_DESCRIPTION,
    "DESCRIPTION": f"{APP_DESCRIPTION} Doc",
    "VERSION": "1.0.0",
    "LICENCE": {"name": "BSD License"},
    "CONTACT": {"name": "Daniel Ale", "email": "d.ale@capitalsage.ng"},
    # Oauth2 related settings. used for example by django-oauth2-toolkit.
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#oauth-flows-object
    "OAUTH2_FLOWS": [],
    "OAUTH2_AUTHORIZATION_URL": None,
    "OAUTH2_TOKEN_URL": None,
    "OAUTH2_REFRESH_URL": None,
    "OAUTH2_SCOPES": None,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
