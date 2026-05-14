from common.audtilog.contrib import get_client_ip
from django.test import RequestFactory


def test_get_client_ip_x_forwarded_for():
    factory = RequestFactory()
    request = factory.get("/", HTTP_X_FORWARDED_FOR="192.168.1.1")
    ip = get_client_ip(request)
    assert ip == "192.168.1.1"


def test_get_client_ip_remote_addr():
    factory = RequestFactory()
    request = factory.get("/", REMOTE_ADDR="127.0.0.1")
    ip = get_client_ip(request)
    assert ip == "127.0.0.1"


def test_get_client_ip_no_ip():
    factory = RequestFactory()
    request = factory.get("/")
    ip = get_client_ip(request)
    assert ip == "127.0.0.1"
