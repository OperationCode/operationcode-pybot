"""Tests for replacing the ALB IP with the real client IP in Sentry events."""

import pytest

from pybot.sentry import (
    before_send,
    before_send_transaction,
    client_ip_from_forwarded_for,
)

ALB_IP = "172.20.15.250"


def make_event(headers, env=None):
    return {
        "request": {
            "headers": headers,
            "env": {"REMOTE_ADDR": ALB_IP} if env is None else env,
        }
    }


@pytest.mark.parametrize(
    ("header", "hops", "expected"),
    [
        ("203.0.113.7", 1, "203.0.113.7"),
        ("1.1.1.1, 203.0.113.7", 1, "203.0.113.7"),  # leftmost entry is client-forged
        ("1.1.1.1, 203.0.113.7", 2, "1.1.1.1"),
        (" 203.0.113.7 , ", 1, "203.0.113.7"),
        ("203.0.113.7", 2, None),
        ("", 1, None),
        ("203.0.113.7", 0, None),
    ],
)
def test_client_ip_from_forwarded_for(header, hops, expected):
    assert client_ip_from_forwarded_for(header, hops) == expected


def test_before_send_uses_forwarded_for():
    event = make_event({"X-Forwarded-For": "198.51.100.1, 203.0.113.7"})
    assert before_send(event, {})["request"]["env"]["REMOTE_ADDR"] == "203.0.113.7"


def test_before_send_header_lookup_is_case_insensitive():
    event = make_event({"x-forwarded-for": "203.0.113.7"})
    assert before_send(event, {})["request"]["env"]["REMOTE_ADDR"] == "203.0.113.7"


def test_before_send_without_header_keeps_remote_addr():
    event = make_event({"User-Agent": "curl/8.7.1"})
    assert before_send(event, {})["request"]["env"]["REMOTE_ADDR"] == ALB_IP


def test_before_send_does_not_add_ip_when_remote_addr_absent():
    """When PII settings removed REMOTE_ADDR, do not add the IP back."""
    event = make_event({"X-Forwarded-For": "203.0.113.7"}, env={})
    assert "REMOTE_ADDR" not in before_send(event, {})["request"]["env"]


def test_before_send_without_request():
    assert before_send({"message": "hi"}, {}) == {"message": "hi"}


def test_before_send_respects_trusted_hops(monkeypatch):
    monkeypatch.setenv("SENTRY_TRUSTED_PROXY_HOPS", "2")
    event = make_event({"X-Forwarded-For": "198.51.100.1, 203.0.113.7"})
    assert before_send(event, {})["request"]["env"]["REMOTE_ADDR"] == "198.51.100.1"


def test_before_send_transaction_uses_forwarded_for():
    event = make_event({"X-Forwarded-For": "203.0.113.7"})
    assert before_send_transaction(event, {})["request"]["env"]["REMOTE_ADDR"] == "203.0.113.7"


def test_before_send_transaction_still_drops_404():
    event = make_event({"X-Forwarded-For": "203.0.113.7"})
    event["contexts"] = {"response": {"status_code": 404}}
    assert before_send_transaction(event, {}) is None


@pytest.mark.parametrize("value", ["abc", "", "0", "-2", "1.5"])
def test_before_send_invalid_hops_falls_back_to_one(monkeypatch, value):
    """A bad SENTRY_TRUSTED_PROXY_HOPS must not raise, or Sentry drops the event."""
    monkeypatch.setenv("SENTRY_TRUSTED_PROXY_HOPS", value)
    event = make_event({"X-Forwarded-For": "198.51.100.1, 203.0.113.7"})
    assert before_send(event, {})["request"]["env"]["REMOTE_ADDR"] == "203.0.113.7"
