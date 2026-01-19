"""Tests for Sentry traces_sampler configuration."""

import pytest

from pybot.sentry import traces_sampler


class TestTracesSampler:
    """Test the traces_sampler function with various contexts."""

    def test_respects_parent_sampled_true(self):
        """Should return 1.0 when parent is sampled."""
        context = {"parent_sampled": True}
        assert traces_sampler(context) == 1.0

    def test_respects_parent_sampled_false(self):
        """Should return 0.0 when parent is not sampled."""
        context = {"parent_sampled": False}
        assert traces_sampler(context) == 0.0

    def test_health_check_by_transaction_name(self):
        """Should sample health check transactions at 1%."""
        context = {"transaction_context": {"name": "pybot.endpoints.handle_health_check"}}
        assert traces_sampler(context) == 0.01

    def test_health_path_in_asgi_scope(self):
        """Should sample /health path at 1%."""
        context = {
            "transaction_context": {"name": "some_handler"},
            "asgi_scope": {"path": "/health"},
        }
        assert traces_sampler(context) == 0.01

    def test_healthz_path_in_asgi_scope(self):
        """Should sample /healthz path at 1%."""
        context = {
            "transaction_context": {"name": "some_handler"},
            "asgi_scope": {"path": "/healthz"},
        }
        assert traces_sampler(context) == 0.01

    def test_liveness_path(self):
        """Should sample liveness endpoints at 1%."""
        context = {"transaction_context": {"name": "liveness_check"}}
        assert traces_sampler(context) == 0.01

    def test_readiness_path(self):
        """Should sample readiness endpoints at 1%."""
        context = {"transaction_context": {"name": "readiness_probe"}}
        assert traces_sampler(context) == 0.01

    def test_normal_transaction_uses_default(self):
        """Should use default sample rate for non-health transactions."""
        context = {"transaction_context": {"name": "pybot.endpoints.slack.handle_event"}}
        # Default is 1.0
        assert traces_sampler(context) == 1.0

    def test_empty_context_uses_default(self):
        """Should use default sample rate for empty context."""
        assert traces_sampler({}) == 1.0

    def test_case_insensitive_matching(self):
        """Should match health patterns case-insensitively."""
        context = {"transaction_context": {"name": "HANDLE_HEALTH_CHECK"}}
        assert traces_sampler(context) == 0.01

    def test_aiohttp_request_object_with_health_path(self):
        """Test with aiohttp_request object (what aiohttp integration actually provides)."""

        # Mock aiohttp Request object with .path attribute
        class MockRequest:
            path = "/health"

        context = {
            "transaction_context": {"name": "generic AIOHTTP request"},
            "aiohttp_request": MockRequest(),
        }
        # Should match on aiohttp_request.path
        assert traces_sampler(context) == 0.01

    def test_aiohttp_request_object_with_healthz_path(self):
        """Test with /healthz path."""

        class MockRequest:
            path = "/healthz"

        context = {
            "transaction_context": {"name": "generic AIOHTTP request"},
            "aiohttp_request": MockRequest(),
        }
        assert traces_sampler(context) == 0.01

    def test_aiohttp_request_object_with_other_path(self):
        """Test that non-health paths get default sample rate."""

        class MockRequest:
            path = "/api/users"

        context = {
            "transaction_context": {"name": "generic AIOHTTP request"},
            "aiohttp_request": MockRequest(),
        }
        # Should NOT match health pattern
        assert traces_sampler(context) == 1.0

    def test_aiohttp_request_object_with_liveness_path(self):
        """Test with /liveness path."""

        class MockRequest:
            path = "/liveness"

        context = {
            "transaction_context": {"name": "generic AIOHTTP request"},
            "aiohttp_request": MockRequest(),
        }
        assert traces_sampler(context) == 0.01

    def test_aiohttp_request_object_with_readiness_path(self):
        """Test with /readiness path."""

        class MockRequest:
            path = "/readiness"

        context = {
            "transaction_context": {"name": "generic AIOHTTP request"},
            "aiohttp_request": MockRequest(),
        }
        assert traces_sampler(context) == 0.01
