import pytest
from common.audtilog.contrib import mask_sensitive_data_v1 as mask_sensitive_data

SENSITIVE_KEYS = [
    "password",
    "token",
    "access",
    "refresh",
    "Authorization",
    "pin",
    "tx_pin",
]


# Test with dictionary data
@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"password": "12345", "user": "test"},
            {"password": "***FILTERED***", "user": "test"},
        ),
        (
            {"token": "abcdef", "details": {"pin": "1234"}},
            {"token": "***FILTERED***", "details": {"pin": "***FILTERED***"}},
        ),
        ({"other_key": "value"}, {"other_key": "value"}),
    ],
)
def test_mask_sensitive_data_dict(data, expected):
    assert mask_sensitive_data(data) == expected


# Test with list data
@pytest.mark.parametrize(
    "data,expected",
    [
        (
            [{"password": "12345"}, {"user": "test"}],
            [{"password": "***FILTERED***"}, {"user": "test"}],
        ),
        (
            [{"token": "abcdef"}, {"details": {"pin": "1234"}}],
            [{"token": "***FILTERED***"}, {"details": {"pin": "***FILTERED***"}}],
        ),
    ],
)
def test_mask_sensitive_data_list(data, expected):
    assert mask_sensitive_data(data) == expected


# Test with string data (URL-like strings)
# @pytest.mark.parametrize(
#     "data,expected",
#     [
#         ("https://example.com?password=12345", "https://example.com?password=***FILTERED***"),
#         ("https://example.com?token=abcdef&user=test", "https://example.com?token=***FILTERED***&user=test"),
#     ],
# )
# def test_mask_sensitive_data_string(data, expected):
#     assert mask_sensitive_data(data) == expected


# Test non-sensitive types (int, None, etc.)
@pytest.mark.parametrize(
    "data",
    [12345, None, True],
)
def test_mask_sensitive_data_passthrough(data):
    assert mask_sensitive_data(data) == data
