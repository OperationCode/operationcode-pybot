"""Tests for validate_request_signature header handling."""

import hashlib
import hmac
import time

import pytest

from pybot._vendor.slack.exceptions import InvalidSlackSignature, InvalidTimestamp
from pybot._vendor.slack.sansio import validate_request_signature

SECRET = "signing-secret"


def _sign(body: str, ts: str) -> str:
    digest = hmac.new(SECRET.encode(), f"v0:{ts}:{body}".encode(), hashlib.sha256).hexdigest()
    return f"v0={digest}"


@pytest.mark.parametrize(
    "headers",
    [
        {"X-Slack-Signature": "v0=x"},
        {"X-Slack-Request-Timestamp": str(int(time.time()))},
        {},
        {"X-Slack-Request-Timestamp": "abc", "X-Slack-Signature": "v0=x"},
    ],
    ids=["missing-timestamp", "missing-signature", "no-headers", "non-numeric-timestamp"],
)
def test_bad_headers_raise_invalid_signature(headers):
    with pytest.raises(InvalidSlackSignature):
        validate_request_signature("{}", headers, SECRET)


def test_valid_signature_passes():
    ts = str(int(time.time()))
    headers = {"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": _sign("{}", ts)}
    validate_request_signature("{}", headers, SECRET)


def test_wrong_signature_raises():
    ts = str(int(time.time()))
    headers = {"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": "v0=bad"}
    with pytest.raises(InvalidSlackSignature):
        validate_request_signature("{}", headers, SECRET)


def test_old_timestamp_raises():
    ts = str(int(time.time()) - 3600)
    headers = {"X-Slack-Request-Timestamp": ts, "X-Slack-Signature": _sign("{}", ts)}
    with pytest.raises(InvalidTimestamp):
        validate_request_signature("{}", headers, SECRET)
