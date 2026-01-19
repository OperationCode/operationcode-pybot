"""
Sentry configuration for pybot.

Provides tracing, profiling, and logging integration following
the same standards as OperationCode/back-end.
"""

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def strtobool(value):
    """Convert string to boolean."""
    if isinstance(value, bool):
        return value
    value_lower = str(value).lower()
    if value_lower in ("true", "1", "yes", "y", "on"):
        return True
    if value_lower in ("false", "0", "no", "n", "off", ""):
        return False
    raise ValueError(f"Cannot convert '{value}' to boolean")


def config(key, default=None, cast=None):
    """Get configuration from environment with optional type casting."""
    value = os.environ.get(key, default)
    if cast is not None and value is not None:
        return cast(value)
    return value


def traces_sampler(sampling_context):
    """
    Custom sampler to control which transactions are traced.
    Returns a sample rate between 0.0 and 1.0.

    Respects parent sampling decisions for distributed tracing.
    """
    logger = logging.getLogger(__name__)

    # Respect parent sampling decision for distributed tracing
    parent_sampled = sampling_context.get("parent_sampled")
    if parent_sampled is not None:
        return float(parent_sampled)

    # Get transaction context
    transaction_context = sampling_context.get("transaction_context", {})
    transaction_name = transaction_context.get("name", "").lower()

    # Get the request path from various possible sources
    request_path = ""

    # Check ASGI scope (for ASGI-based frameworks)
    asgi_scope = sampling_context.get("asgi_scope", {})
    if asgi_scope:
        request_path = asgi_scope.get("path", "").lower()

    # Check WSGI environ (for WSGI-based frameworks like Django)
    wsgi_environ = sampling_context.get("wsgi_environ", {})
    if wsgi_environ and not request_path:
        request_path = wsgi_environ.get("PATH_INFO", "").lower()

    # Check aiohttp_request (for aiohttp - this is the actual Request object)
    aiohttp_request = sampling_context.get("aiohttp_request")
    if aiohttp_request is not None:
        try:
            request_path = str(aiohttp_request.path).lower()
        except Exception:
            pass

    # Debug logging to understand what context is being passed
    logger.debug(
        "traces_sampler called: transaction_name=%s, request_path=%s, context_keys=%s",
        transaction_name,
        request_path,
        list(sampling_context.keys()),
    )

    # Sample health check endpoints at 1% (to catch errors but reduce noise)
    # Check both URL paths and handler function names
    health_patterns = ["healthz", "health", "readiness", "liveness", "health_check"]
    if request_path and any(pattern in request_path for pattern in health_patterns):
        logger.debug("Sampling health check path at 1%%: %s", request_path)
        return 0.01
    if any(pattern in transaction_name for pattern in health_patterns):
        logger.debug("Sampling health check transaction at 1%%: %s", transaction_name)
        return 0.01

    # Use the configured sample rate for everything else
    return config("SENTRY_TRACES_SAMPLE_RATE", default=1.0, cast=float)


def before_send_transaction(event, hint):  # noqa: ARG001
    """
    Filter transactions before sending to Sentry.
    Returns None to drop the transaction, or the event to send it.

    Args:
        event: The transaction event
        hint: Additional context (unused but required by Sentry signature)
    """
    # Drop 404 transactions (not found errors are noise, not actionable issues)
    if event.get("contexts", {}).get("response", {}).get("status_code") == 404:
        return None

    return event


def init_sentry():
    """
    Initialize Sentry with tracing, profiling, and logging.

    Only initializes if SENTRY_DSN is set in environment.
    """
    sentry_dsn = config("SENTRY_DSN", default="")

    if not sentry_dsn:
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            AioHttpIntegration(),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors and above as events
            ),
        ],
        environment=config("ENVIRONMENT", default="production"),
        release=config("VERSION", default="1.0.0"),
        # Performance Monitoring (Tracing) - use custom sampler to filter health checks
        traces_sampler=traces_sampler,
        # Filter transactions before sending (e.g., drop 404s)
        before_send_transaction=before_send_transaction,
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=config("SENTRY_PROFILES_SAMPLE_RATE", default=1.0, cast=float),
        # Send default PII like user IP and user ID to Sentry
        send_default_pii=config("SENTRY_SEND_DEFAULT_PII", default=True, cast=strtobool),
    )
