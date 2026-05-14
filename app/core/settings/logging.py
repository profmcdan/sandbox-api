import logging
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", '
            '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(asctime)s:%(log_color)s%(levelname)s:%(name)s:%(message)s ------------",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "verbose": {
            "format": (
                "\n--- %(levelname)s ---\n"
                "Timestamp: %(asctime)s\n"
                "Message: %(message)s\n"
                "Location: %(pathname)s:%(lineno)d in %(funcName)s\n"
                "-------------------------------------------------\n"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        # Catch all Django-related logs here
        "django": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    # Root logger for all other logs
    "root": {
        "handlers": [
            "console",
        ],
        "level": "INFO",
    },
}

DEBUG = int(os.environ.get("DEBUG", 1))
if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(level=logging.ERROR, event_level=logging.ERROR),
        ],
        traces_sample_rate=1.0,
        send_default_pii=False,
        environment=os.environ.get("ENVIRONMENT_INSTANCE"),
    )

DRF_API_LOGGER_EXCLUDE_KEYS = [
    "tx_pin",
    "bvn",
    "nin",
    "X-KMS-KEY",
    "Authorization",
    "transaction_pin",
]
MONGODB_LOGGER_URL = os.getenv("MONGODB_LOGGER_URL")
MONGODB_LOGGER_DATABASE = os.getenv("APP_NAME")

# OpenSearch
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_PORT = 9200

# Optional
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")
OPENSEARCH_USE_SSL = False

OPENSEARCH_INDEX = "sandbox-api"
