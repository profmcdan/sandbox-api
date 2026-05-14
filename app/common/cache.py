import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


def read_from_cache(key):
    try:
        return cache.get(key)
    except Exception as e:
        logger.error(f"REDIS read error: {e}")
    return None


def write_to_cache(key, value, timeout=60 * 60 * 6):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception as e:
        logger.error(f"REDIS write error: {e}")


def delete_from_cache(key):
    try:
        cache.delete(key)
    except Exception as e:
        logger.error(f"REDIS delete error: {e}")


def clear_cache():
    try:
        cache.clear()
    except Exception as e:
        logger.error(f"REDIS clear error: {e}")
