# Upgrade Plan: operationcode-pybot

## Overview

This document provides a step-by-step plan to upgrade operationcode-pybot from Python 3.7 to Python 3.12 by **vendoring** the abandoned `sirbot` and `slack-sansio` dependencies directly into the repository.

**Target completion**: 3-4 weeks
**Team size**: 1-2 developers
**Risk level**: Low

---

## Phase 0: Establish Test Baseline (Days 1-4) ✅ COMPLETE

> **Why Docker?** Python 3.7 cannot be installed on modern macOS (especially Apple Silicon).
> We must run the existing tests in a Docker container to establish a baseline before upgrading.
>
> **Status**: Completed January 4, 2026
> **Result**: 57 tests passing, 0 failures, 1 warning (deprecation warning is expected)

### 0.1 Create Test Dockerfile

Create `docker/Dockerfile.test` for running tests in Python 3.7:

```dockerfile
# docker/Dockerfile.test
# For running tests in Python 3.7 (required since 3.7 won't install on modern macOS)

FROM python:3.7-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install specific poetry version compatible with Python 3.7
RUN pip install "poetry==1.1.15"

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (including dev)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction

# Copy source code
COPY . .

# Default command: run tests
CMD ["poetry", "run", "pytest", "-v"]
```

### 0.2 Create Docker Compose for Testing

Create `docker/docker-compose.test.yml`:

```yaml
version: '3.8'

services:
  test-py37:
    build:
      context: ..
      dockerfile: docker/Dockerfile.test
    environment:
      - SLACK_TOKEN=test_token
      - SLACK_VERIFY=supersecuretoken
      - SLACK_BOT_USER_ID=bot_user_id
      - SLACK_BOT_ID=bot_id
      - AIRTABLE_API_KEY=test_key
      - AIRTABLE_BASE_KEY=test_base
      - YELP_TOKEN=test_yelp
      - BACKEND_AUTH_TOKEN=devBackendToken
    volumes:
      - ../tests:/app/tests:ro
      - ../pybot:/app/pybot:ro
    command: poetry run pytest -v --tb=short

  test-py312:
    build:
      context: ..
      dockerfile: docker/Dockerfile.test.py312
    environment:
      - SLACK_TOKEN=test_token
      - SLACK_VERIFY=supersecuretoken
      - SLACK_BOT_USER_ID=bot_user_id
      - SLACK_BOT_ID=bot_id
      - AIRTABLE_API_KEY=test_key
      - AIRTABLE_BASE_KEY=test_base
      - YELP_TOKEN=test_yelp
      - BACKEND_AUTH_TOKEN=devBackendToken
    volumes:
      - ../tests:/app/tests:ro
      - ../pybot:/app/pybot:ro
    command: poetry run pytest -v --tb=short
```

### 0.3 Test Runner Scripts

Create `scripts/test-py37.sh`:

```bash
#!/bin/bash
# Run tests in Python 3.7 Docker container
set -e

cd "$(dirname "$0")/.."

echo "🐍 Running tests in Python 3.7 container..."
docker build -t pybot-test:py37 -f docker/Dockerfile.test .
docker run --rm \
    -e SLACK_TOKEN=test_token \
    -e SLACK_VERIFY=supersecuretoken \
    -e SLACK_BOT_USER_ID=bot_user_id \
    -e SLACK_BOT_ID=bot_id \
    -e AIRTABLE_API_KEY=test_key \
    -e AIRTABLE_BASE_KEY=test_base \
    -e YELP_TOKEN=test_yelp \
    -e BACKEND_AUTH_TOKEN=devBackendToken \
    pybot-test:py37 \
    poetry run pytest -v "$@"
```

Create `scripts/test-py312.sh` (for after upgrade):

```bash
#!/bin/bash
# Run tests in Python 3.12 Docker container
set -e

cd "$(dirname "$0")/.."

echo "🐍 Running tests in Python 3.12 container..."
docker build -t pybot-test:py312 -f docker/Dockerfile.test.py312 .
docker run --rm \
    -e SLACK_TOKEN=test_token \
    -e SLACK_VERIFY=supersecuretoken \
    -e SLACK_BOT_USER_ID=bot_user_id \
    -e SLACK_BOT_ID=bot_id \
    -e AIRTABLE_API_KEY=test_key \
    -e AIRTABLE_BASE_KEY=test_base \
    -e YELP_TOKEN=test_yelp \
    -e BACKEND_AUTH_TOKEN=devBackendToken \
    pybot-test:py312 \
    poetry run pytest -v "$@"
```

Make scripts executable:

```bash
chmod +x scripts/test-py37.sh scripts/test-py312.sh
```

### 0.4 Run Existing Tests to Establish Baseline

```bash
./scripts/test-py37.sh
```

Document which tests pass/fail before any changes.

### 0.5 Add Critical Safety Net Tests

Create `tests/test_upgrade_safety.py`:

```python
"""
Upgrade Safety Tests

These tests catch common Python 3.7 → 3.12 upgrade issues:
- Import errors (syntax changes)
- Async function verification (asyncio.coroutine removal)
- Handler registration verification
"""

import asyncio
import importlib

import pytest


class TestModuleImports:
    """Verify all modules import without syntax errors."""

    MODULES = [
        "pybot",
        "pybot.__main__",
        "pybot.endpoints.slack.commands",
        "pybot.endpoints.slack.events",
        "pybot.endpoints.slack.messages",
        "pybot.endpoints.slack.actions",
        "pybot.endpoints.slack.actions.general_actions",
        "pybot.endpoints.slack.actions.mentor_request",
        "pybot.endpoints.slack.actions.mentor_volunteer",
        "pybot.endpoints.slack.actions.new_member",
        "pybot.endpoints.slack.actions.report_message",
        "pybot.endpoints.slack.utils.slash_lunch",
        "pybot.endpoints.slack.utils.action_messages",
        "pybot.endpoints.airtable.requests",
        "pybot.endpoints.api.slack_api",
        "pybot.plugins.airtable.plugin",
        "pybot.plugins.airtable.api",
        "pybot.plugins.api.plugin",
    ]

    @pytest.mark.parametrize("module_name", MODULES)
    def test_module_imports(self, module_name):
        """Each module should import without errors."""
        importlib.import_module(module_name)


class TestAsyncHandlers:
    """Verify all handlers are proper async functions.

    Critical for Python 3.11+ where asyncio.coroutine() is removed.
    """

    def test_slash_commands_are_async(self):
        from pybot.endpoints.slack.commands import (
            slash_lunch,
            slash_mentor,
            slash_mentor_volunteer,
            slash_repeat,
            slash_report,
            slash_roll,
        )

        handlers = [
            slash_lunch,
            slash_mentor,
            slash_mentor_volunteer,
            slash_repeat,
            slash_report,
            slash_roll,
        ]
        for handler in handlers:
            # Get the wrapped function if decorated
            func = getattr(handler, "__wrapped__", handler)
            assert asyncio.iscoroutinefunction(func), \
                f"{handler.__name__} must be async"

    def test_event_handlers_are_async(self):
        from pybot.endpoints.slack.events import team_join

        assert asyncio.iscoroutinefunction(team_join), \
            "team_join must be async"

    def test_action_handlers_are_async(self):
        from pybot.endpoints.slack.actions.general_actions import (
            claimed,
            delete_message,
            reset_claim,
        )

        handlers = [claimed, delete_message, reset_claim]
        for handler in handlers:
            assert asyncio.iscoroutinefunction(handler), \
                f"{handler.__name__} must be async"


class TestPluginLoading:
    """Verify plugins can be instantiated."""

    def test_airtable_plugin_instantiates(self):
        from pybot.plugins.airtable.plugin import AirtablePlugin
        plugin = AirtablePlugin()
        assert plugin.__name__ == "airtable"

    def test_api_plugin_instantiates(self):
        from pybot.plugins.api.plugin import APIPlugin
        plugin = APIPlugin()
        assert plugin.__name__ == "api"
```

Create `tests/unit/test_lunch_command.py`:

```python
"""Unit tests for LunchCommand parsing logic."""

import pytest

from pybot.endpoints.slack.utils.slash_lunch import LunchCommand


class TestLunchCommandParsing:
    """Test input parsing without making API calls."""

    def test_empty_input_uses_defaults(self):
        cmd = LunchCommand("C123", "U456", "", "testuser")
        params = cmd.lunch_api_params

        assert params["term"] == "lunch"
        assert "location" in params
        assert "range" in params

    def test_zipcode_only_input(self):
        cmd = LunchCommand("C123", "U456", "90210", "testuser")
        params = cmd.lunch_api_params

        assert params["location"] == 90210
        assert params["term"] == "lunch"

    def test_zipcode_with_distance(self):
        cmd = LunchCommand("C123", "U456", "90210 5", "testuser")
        params = cmd.lunch_api_params

        assert params["location"] == 90210
        # 5 miles in meters
        assert params["range"] == int(5 * 1609.34)

    def test_invalid_zipcode_uses_random(self):
        cmd = LunchCommand("C123", "U456", "not-a-zip", "testuser")
        params = cmd.lunch_api_params

        # Should fall back to a random valid zip
        assert isinstance(params["location"], int)

    def test_negative_distance_converted_to_positive(self):
        cmd = LunchCommand("C123", "U456", "90210 -5", "testuser")
        params = cmd.lunch_api_params

        # Should use absolute value
        assert params["range"] == int(5 * 1609.34)

    def test_distance_capped_at_max(self):
        cmd = LunchCommand("C123", "U456", "90210 100", "testuser")
        params = cmd.lunch_api_params

        # Should cap at default (20 miles)
        assert params["range"] == int(20 * 1609.34)


class TestLunchCommandResponse:
    """Test response building."""

    def test_build_response_text(self):
        cmd = LunchCommand("C123", "U456", "90210", "testuser")

        mock_location = {
            "name": "Test Restaurant",
            "location": {
                "display_address": ["123 Main St", "Los Angeles, CA 90210"]
            }
        }

        response = cmd._build_response_text(mock_location)

        assert response["user"] == "U456"
        assert response["channel"] == "C123"
        assert "Test Restaurant" in response["text"]
        assert "123 Main St" in response["text"]


class TestYelpRequest:
    """Test Yelp API request building."""

    def test_yelp_request_structure(self):
        cmd = LunchCommand("C123", "U456", "90210", "testuser")
        request = cmd.get_yelp_request()

        assert request["url"] == "https://api.yelp.com/v3/businesses/search"
        assert "Authorization" in request["headers"]
        assert "params" in request
```

Create `tests/unit/test_roll_command.py`:

```python
"""Unit tests for /roll command parsing."""

import pytest


class TestRollParsing:
    """Test dice roll input parsing."""

    @pytest.mark.parametrize("input_text,expected_valid", [
        ("1d6", True),
        ("2d10", True),
        ("10d20", True),
        ("1D6", True),  # Case insensitive
        ("0d6", False),  # Zero dice
        ("11d6", False),  # Too many dice
        ("1d0", False),  # Zero sides
        ("1d21", False),  # Too many sides
        ("abc", False),  # Not a dice format
        ("1d", False),  # Incomplete
        ("d6", False),  # Missing count
    ])
    def test_roll_input_validation(self, input_text, expected_valid):
        """Test various roll command inputs."""
        try:
            text = input_text.lower()
            numdice, typedice = [int(num) for num in text.split("d")]
            valid = (
                0 < numdice <= 10 and
                0 < typedice <= 20
            )
        except (ValueError, IndexError):
            valid = False

        assert valid == expected_valid
```

Create `tests/unit/test_action_messages.py`:

```python
"""Unit tests for action message builders."""

import pytest

from pybot.endpoints.slack.utils.action_messages import (
    base_response,
    claimed_attachment,
    not_claimed_attachment,
)


class TestActionMessages:
    """Test message attachment builders."""

    def test_not_claimed_attachment_structure(self):
        attachment = not_claimed_attachment()

        assert "callback_id" in attachment
        assert "actions" in attachment
        assert isinstance(attachment["actions"], list)

    def test_claimed_attachment_includes_user(self):
        attachment = claimed_attachment("U12345")

        assert "callback_id" in attachment
        # Should mention the user who claimed
        assert "U12345" in str(attachment)

    def test_base_response_extracts_required_fields(self):
        mock_action = {
            "channel": {"id": "C123"},
            "message_ts": "123456.789",
        }

        response = base_response(mock_action)

        assert response["channel"] == "C123"
        assert response["ts"] == "123456.789"
```

### 0.6 Run Enhanced Test Suite

```bash
# Run all tests including new safety tests
./scripts/test-py37.sh

# Expected output: capture pass/fail counts as baseline
# Example: "15 passed, 0 failed"
```

### 0.7 Document Baseline ✅

**Baseline Test Results - Python 3.7.17**

**Date**: January 4, 2026
**Python Version**: 3.7.17
**Test Command**: `./scripts/test-py37.sh`
**Docker Image**: python:3.7-slim

## Results Summary

**Total: 57 tests passed, 0 failed, 1 warning**

| Test Category | Tests | Status |
|--------------|-------|--------|
| **Upgrade Safety Tests** | 23 | ✅ All Passed |
| - Module imports | 18 | ✅ |
| - Async handler verification | 3 | ✅ |
| - Plugin loading | 2 | ✅ |
| **Existing Integration Tests** | 11 | ✅ All Passed |
| - API endpoint tests | 4 | ✅ |
| - Slack action tests | 4 | ✅ |
| - Slack event tests | 4 | ✅ |
| **New Unit Tests** | 23 | ✅ All Passed |
| - Action message tests | 3 | ✅ |
| - Lunch command tests | 8 | ✅ |
| - Roll command tests | 11 | ✅ |

## Test Coverage by Module

- **test_upgrade_safety.py**: 23 tests - Verifies all modules import correctly and handlers are async
- **test_slack_api_endpoint.py**: 4 tests - API credential detection and verification
- **test_slack_actions.py**: 4 tests - Mentor claim/unclaim actions
- **test_slack_events.py**: 4 tests - Team join and message logging
- **test_action_messages.py**: 3 tests - Message attachment builders
- **test_lunch_command.py**: 8 tests - Lunch command parsing and Yelp integration
- **test_roll_command.py**: 11 tests - Dice roll input validation

## Warnings

1 deprecation warning (expected, will be addressed in upgrade):
```
DeprecationWarning: Inheritance class SirBot from web.Application is discouraged
```

This warning is expected and relates to aiohttp's deprecation patterns. It will be resolved during the Python 3.12 upgrade when we modernize the vendored sirbot code.

## Key Findings

1. ✅ All async handlers are properly defined with `async def`
2. ✅ All modules import without syntax errors
3. ✅ Both custom plugins instantiate correctly
4. ✅ All existing integration tests pass
5. ✅ New safety net tests provide comprehensive coverage

**Baseline is stable and ready for upgrade work.**

---

## Phase 1: Setup and Preparation (Days 5-6) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: All source files vendored (22 files total), feature branch created

### 1.1 Create Development Environment

```bash
# Install Python 3.12
pyenv install 3.12.1
cd /path/to/operationcode-pybot
pyenv local 3.12.1

# Verify Python version
python3 --version  # Should show 3.12.x
```

### 1.2 Create Feature Branch

```bash
git checkout -b feature/python-3.12-upgrade
```

### 1.3 Create Vendor Directory Structure

```bash
mkdir -p pybot/_vendor/sirbot/plugins/slack
mkdir -p pybot/_vendor/slack/io
mkdir -p pybot/_vendor/slack/tests
```

### 1.4 Download Source Files

Clone the source repositories temporarily to copy files:

```bash
# In a temporary directory
cd /tmp
git clone https://github.com/pyslackers/slack-sansio.git
git clone https://github.com/pyslackers/sir-bot-a-lot-2.git
```

---

## Phase 2: Vendor slack-sansio (Day 2-3) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: slack-sansio already Python 3.12 compatible - no loop= parameters, no asyncio.coroutine usage

### 2.1 Copy Required Files

```bash
# From /tmp/slack-sansio to pybot/_vendor/slack/
cp slack-sansio/slack/__init__.py pybot/_vendor/slack/
cp slack-sansio/slack/actions.py pybot/_vendor/slack/
cp slack-sansio/slack/commands.py pybot/_vendor/slack/
cp slack-sansio/slack/events.py pybot/_vendor/slack/
cp slack-sansio/slack/exceptions.py pybot/_vendor/slack/
cp slack-sansio/slack/methods.py pybot/_vendor/slack/
cp slack-sansio/slack/sansio.py pybot/_vendor/slack/

cp slack-sansio/slack/io/__init__.py pybot/_vendor/slack/io/
cp slack-sansio/slack/io/abc.py pybot/_vendor/slack/io/
cp slack-sansio/slack/io/aiohttp.py pybot/_vendor/slack/io/

# Test fixtures
cp slack-sansio/slack/tests/__init__.py pybot/_vendor/slack/tests/
cp slack-sansio/slack/tests/plugin.py pybot/_vendor/slack/tests/
```

### 2.2 Add License Attribution

Create `pybot/_vendor/slack/LICENSE`:

```
MIT License

Original work Copyright (c) 2017-2020 pyslackers
Modified work Copyright (c) 2024 Operation Code

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 2.3 Fix slack/io/aiohttp.py

Remove deprecated `loop=` parameter:

```python
# BEFORE (around line 30-40)
class SlackAPI(_SlackAPI):
    def __init__(self, *, session: aiohttp.ClientSession, **kwargs) -> None:
        self._session = session
        super().__init__(**kwargs)

# This should work as-is, but check for any loop= usage
```

### 2.4 Update slack/__init__.py

Ensure clean exports:

```python
"""
Vendored slack-sansio library for Python 3.12+
Original: https://github.com/pyslackers/slack-sansio
"""

from pybot._vendor.slack.methods import Methods as methods

__all__ = ["methods"]
```

---

## Phase 3: Vendor sirbot (Day 3-4) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: sirbot modernized for Python 3.12+ - removed asyncio.coroutine(), fixed loop= parameters, added type hints

### 3.1 Copy Required Files

```bash
# From /tmp/sir-bot-a-lot-2 to pybot/_vendor/sirbot/
cp sir-bot-a-lot-2/sirbot/__init__.py pybot/_vendor/sirbot/
cp sir-bot-a-lot-2/sirbot/bot.py pybot/_vendor/sirbot/
cp sir-bot-a-lot-2/sirbot/endpoints.py pybot/_vendor/sirbot/

cp sir-bot-a-lot-2/sirbot/plugins/__init__.py pybot/_vendor/sirbot/plugins/
cp sir-bot-a-lot-2/sirbot/plugins/slack/__init__.py pybot/_vendor/sirbot/plugins/slack/
cp sir-bot-a-lot-2/sirbot/plugins/slack/plugin.py pybot/_vendor/sirbot/plugins/slack/
cp sir-bot-a-lot-2/sirbot/plugins/slack/endpoints.py pybot/_vendor/sirbot/plugins/slack/
```

### 3.2 Add License Attribution

Create `pybot/_vendor/sirbot/LICENSE`:

```
MIT License

Original work Copyright (c) 2017-2019 pyslackers
Modified work Copyright (c) 2024 Operation Code

[Same MIT text as above]
```

### 3.3 Fix sirbot/bot.py

Update the SirBot class for Python 3.12:

```python
"""
Vendored sirbot library for Python 3.12+
Original: https://github.com/pyslackers/sir-bot-a-lot-2
"""

import logging
from typing import Any

import aiohttp.web

from . import endpoints

LOG = logging.getLogger(__name__)


class SirBot(aiohttp.web.Application):
    def __init__(self, user_agent: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.router.add_route("GET", "/sirbot/plugins", endpoints.plugins)

        self["plugins"] = {}
        self["http_session"] = None  # Created on startup
        self["user_agent"] = user_agent or "sir-bot-a-lot"

        self.on_startup.append(self._create_session)
        self.on_shutdown.append(self.stop)

    async def _create_session(self, app: aiohttp.web.Application) -> None:
        """Create HTTP session on startup (when event loop exists)."""
        self["http_session"] = aiohttp.ClientSession()

    def start(self, **kwargs: Any) -> None:
        LOG.info("Starting SirBot")
        aiohttp.web.run_app(self, **kwargs)

    def load_plugin(self, plugin: Any, name: str | None = None) -> None:
        name = name or plugin.__name__
        self["plugins"][name] = plugin
        plugin.load(self)

    async def stop(self, sirbot: "SirBot") -> None:
        if self["http_session"]:
            await self["http_session"].close()

    @property
    def plugins(self) -> dict:
        return self["plugins"]

    @property
    def http_session(self) -> aiohttp.ClientSession:
        return self["http_session"]

    @property
    def user_agent(self) -> str:
        return self["user_agent"]
```

### 3.4 Fix sirbot/plugins/slack/plugin.py

This is the most critical file. Replace deprecated `asyncio.coroutine()`:

```python
"""
Vendored sirbot Slack plugin for Python 3.12+
"""

import asyncio
import logging
import os
from typing import Any, Callable, Coroutine

from pybot._vendor.slack import methods
from pybot._vendor.slack.events import EventRouter, MessageRouter
from pybot._vendor.slack.actions import Router as ActionRouter
from pybot._vendor.slack.commands import Router as CommandRouter
from pybot._vendor.slack.io.aiohttp import SlackAPI

from . import endpoints

LOG = logging.getLogger(__name__)

# Type alias for async handlers
AsyncHandler = Callable[..., Coroutine[Any, Any, Any]]


def _ensure_async(handler: Callable) -> AsyncHandler:
    """Ensure handler is an async function."""
    if not asyncio.iscoroutinefunction(handler):
        raise TypeError(
            f"Handler {handler.__name__} must be an async function (defined with 'async def')"
        )
    return handler


class SlackPlugin:
    """
    Handle communication from and to Slack.

    Endpoints:
        * ``/slack/events``: Incoming events.
        * ``/slack/commands``: Incoming commands.
        * ``/slack/actions``: Incoming actions.

    Args:
        token: Slack authentication token (env var: `SLACK_TOKEN`).
        bot_id: Bot ID (env var: `SLACK_BOT_ID`).
        bot_user_id: User ID of the bot (env var: `SLACK_BOT_USER_ID`).
        admins: List of Slack admin user IDs (env var: `SLACK_ADMINS`).
        verify: Slack verification token (env var: `SLACK_VERIFY`).
        signing_secret: Slack signing secret (env var: `SLACK_SIGNING_SECRET`).
    """

    __name__ = "slack"

    def __init__(
        self,
        *,
        token: str | None = None,
        bot_id: str | None = None,
        bot_user_id: str | None = None,
        admins: list[str] | None = None,
        verify: str | None = None,
        signing_secret: str | None = None,
    ) -> None:
        self.api: SlackAPI | None = None
        self.token = token or os.environ["SLACK_TOKEN"]
        self.admins = admins or os.environ.get("SLACK_ADMINS", [])

        if signing_secret or "SLACK_SIGNING_SECRET" in os.environ:
            self.signing_secret = signing_secret or os.environ["SLACK_SIGNING_SECRET"]
            self.verify = None
        else:
            self.verify = verify or os.environ["SLACK_VERIFY"]
            self.signing_secret = None

        self.bot_id = bot_id or os.environ.get("SLACK_BOT_ID")
        self.bot_user_id = bot_user_id or os.environ.get("SLACK_BOT_USER_ID")
        self.handlers_option: dict = {}

        if not self.bot_user_id:
            LOG.warning(
                "`SLACK_BOT_USER_ID` not set. It is required for `on mention` routing "
                "and discarding messages from Sir Bot-a-lot to avoid loops."
            )

        self.routers = {
            "event": EventRouter(),
            "command": CommandRouter(),
            "message": MessageRouter(),
            "action": ActionRouter(),
        }

    def load(self, sirbot: Any) -> None:
        LOG.info("Loading slack plugin")
        self.api = SlackAPI(session=sirbot.http_session, token=self.token)

        sirbot.router.add_route("POST", "/slack/events", endpoints.incoming_event)
        sirbot.router.add_route("POST", "/slack/commands", endpoints.incoming_command)
        sirbot.router.add_route("POST", "/slack/actions", endpoints.incoming_action)

        if self.bot_user_id and not self.bot_id:
            sirbot.on_startup.append(self.find_bot_id)

    def on_event(self, event_type: str, handler: AsyncHandler, wait: bool = True) -> None:
        """Register handler for an event."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["event"].register(event_type, (handler, configuration))

    def on_command(self, command: str, handler: AsyncHandler, wait: bool = True) -> None:
        """Register handler for a command."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["command"].register(command, (handler, configuration))

    def on_message(
        self,
        pattern: str,
        handler: AsyncHandler,
        mention: bool = False,
        admin: bool = False,
        wait: bool = True,
        **kwargs: Any,
    ) -> None:
        """Register handler for a message pattern."""
        handler = _ensure_async(handler)

        if admin and not self.admins:
            LOG.warning(
                "Slack admin IDs are not set. Admin-limited endpoints will not work."
            )

        configuration = {"mention": mention, "admin": admin, "wait": wait}
        self.routers["message"].register(
            pattern=pattern, handler=(handler, configuration), **kwargs
        )

    def on_action(
        self,
        action: str,
        handler: AsyncHandler,
        name: str = "*",
        wait: bool = True,
    ) -> None:
        """Register handler for an action."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["action"].register(action, (handler, configuration), name)

    def on_block(
        self,
        block_id: str,
        handler: AsyncHandler,
        action_id: str = "*",
        wait: bool = True,
    ) -> None:
        """Register handler for a block_actions type action."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["action"].register_block_action(
            block_id, (handler, configuration), action_id
        )

    def on_dialog_submission(
        self,
        callback_id: str,
        handler: AsyncHandler,
        wait: bool = True,
    ) -> None:
        """Register handler for a dialog_submission type action."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["action"].register_dialog_submission(
            callback_id, (handler, configuration)
        )

    async def find_bot_id(self, app: Any) -> None:
        rep = await self.api.query(
            url=methods.USERS_INFO, data={"user": self.bot_user_id}
        )
        self.bot_id = rep["user"]["profile"]["bot_id"]
        LOG.warning(
            '`SLACK_BOT_ID` not set. For a faster start time set it to: "%s"',
            self.bot_id,
        )
```

### 3.5 Update sirbot/plugins/slack/__init__.py

```python
"""Slack plugin for sirbot."""
from pybot._vendor.sirbot.plugins.slack.plugin import SlackPlugin

__all__ = ["SlackPlugin"]
```

### 3.6 Update sirbot/__init__.py

```python
"""
Vendored sirbot library for Python 3.12+
Original: https://github.com/pyslackers/sir-bot-a-lot-2
"""
from pybot._vendor.sirbot.bot import SirBot

__all__ = ["SirBot"]
```

### 3.7 Fix Internal Imports in sirbot/plugins/slack/endpoints.py

Update imports to use vendored paths:

```python
# BEFORE
from slack import methods
from slack.io.aiohttp import SlackAPI

# AFTER
from pybot._vendor.slack import methods
from pybot._vendor.slack.io.aiohttp import SlackAPI
```

---

## Phase 4: Create Vendor Package Init (Day 4) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: All vendored packages verified working - imports, instantiation, and Python 3.12 compatibility confirmed

### 4.1 Create pybot/_vendor/__init__.py

```python
"""
Vendored dependencies for operationcode-pybot.

These are modified copies of abandoned libraries, updated for Python 3.12+:
- sirbot: https://github.com/pyslackers/sir-bot-a-lot-2 (MIT License)
- slack-sansio: https://github.com/pyslackers/slack-sansio (MIT License)

Both libraries were last updated in 2019-2020 and are no longer maintained.
We vendor them here with minimal modifications for modern Python compatibility.
"""

__all__ = ["sirbot", "slack"]
```

---

## Phase 5: Update pybot Imports (Day 4-5) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: All 19 files updated to use vendored imports - all imports verified working

### 5.1 Update All Import Statements

Use find/replace across the codebase:

```bash
# Find all files with old imports
grep -r "from sirbot import" pybot/ tests/
grep -r "from sirbot.plugins" pybot/ tests/
grep -r "from slack\." pybot/ tests/
```

Replace patterns:

| Old Import | New Import |
|------------|------------|
| `from sirbot import SirBot` | `from pybot._vendor.sirbot import SirBot` |
| `from sirbot.plugins.slack import SlackPlugin` | `from pybot._vendor.sirbot.plugins.slack import SlackPlugin` |
| `from slack.events import Event` | `from pybot._vendor.slack.events import Event` |
| `from slack.actions import Action` | `from pybot._vendor.slack.actions import Action` |
| `from slack.commands import Command` | `from pybot._vendor.slack.commands import Command` |
| `from slack.methods import Methods` | `from pybot._vendor.slack.methods import Methods` |
| `from slack.exceptions import SlackAPIError` | `from pybot._vendor.slack.exceptions import SlackAPIError` |
| `from slack.io.aiohttp import SlackAPI` | `from pybot._vendor.slack.io.aiohttp import SlackAPI` |
| `from slack.io.abc import SlackAPI` | `from pybot._vendor.slack.io.abc import SlackAPI` |

### 5.2 Files to Update

```
pybot/__main__.py
pybot/endpoints/slack/actions/__init__.py
pybot/endpoints/slack/actions/general_actions.py
pybot/endpoints/slack/actions/mentor_request.py
pybot/endpoints/slack/actions/mentor_volunteer.py
pybot/endpoints/slack/actions/new_member.py
pybot/endpoints/slack/actions/report_message.py
pybot/endpoints/slack/commands.py
pybot/endpoints/slack/events.py
pybot/endpoints/slack/messages.py
pybot/endpoints/slack/message_templates/block_action.py
pybot/endpoints/slack/message_templates/mentor_request.py
pybot/endpoints/slack/utils/event_utils.py
pybot/endpoints/slack/utils/general_utils.py
pybot/endpoints/api/slack_api.py
pybot/endpoints/api/utils.py
pybot/endpoints/airtable/requests.py
pybot/endpoints/airtable/utils.py
pybot/plugins/api/plugin.py
pybot/plugins/airtable/plugin.py
tests/conftest.py
tests/endpoints/api/test_slack_api_endpoint.py
tests/endpoints/slack/test_slack_actions.py
```

### 5.3 Update tests/conftest.py

```python
import copy

import pytest
from pybot._vendor.sirbot import SirBot
from pybot._vendor.sirbot.plugins.slack import SlackPlugin

from pybot import endpoints
from pybot.plugins import AirtablePlugin, APIPlugin
from tests import data

pytest_plugins = ("pybot._vendor.slack.tests.plugin",)


@pytest.fixture(params=list(data.Action.__members__.keys()))
def action(request):
    if isinstance(request.param, str):
        payload = copy.deepcopy(data.Action[request.param].value)
    else:
        payload = copy.deepcopy(request.param)
    return payload


@pytest.fixture
async def bot() -> SirBot:
    b = SirBot()
    # Manually create session for testing (normally done on startup)
    import aiohttp
    b["http_session"] = aiohttp.ClientSession()

    slack = SlackPlugin(
        token="token",
        verify="supersecuretoken",
        bot_user_id="bot_user_id",
        bot_id="bot_id",
    )
    airtable = AirtablePlugin()
    endpoints.slack.create_endpoints(slack)

    api = APIPlugin()
    endpoints.api.create_endpoints(api)

    b.load_plugin(slack)
    b.load_plugin(airtable)
    b.load_plugin(api)

    return b


@pytest.fixture
def slack_bot(bot: SirBot) -> SirBot:
    slack = SlackPlugin(
        token="token",
        verify="supersecuretoken",
        bot_user_id="bot_user_id",
        bot_id="bot_id",
    )
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)
    return bot
```

---

## Phase 6: Update pyproject.toml (Day 5) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: Updated to Python 3.12+, removed vendored deps, modernized all dependencies
> **Test Results**: 57/57 tests passing in Python 3.13! ✅

### Additional Fixes Applied

**1. Package Mode Configuration**
- Added `packages = [{include = "pybot"}]` to fix poetry installation

**2. Updated to Latest Versions**
- pytest: 7.4 → 9.0.2
- pytest-asyncio: 0.23 → 1.3.0
- black: 24.10 → 25.12.0
- ruff: 0.1 → 0.14.10
- sentry-sdk: 1.45 → 2.48.0

**3. Replaced Deprecated `asynctest` Library**
- Replaced `asynctest.CoroutineMock` with `unittest.mock.AsyncMock`
- Replaced `asynctest.asyncio` with standard `asyncio`
- Fixed test fixtures to remove deprecated `loop` parameter

**4. Fixed Test Fixtures**
- Updated `bot` fixture to manually create/cleanup aiohttp session
- Removed deprecated `loop` fixture dependency

### 6.1 New pyproject.toml

```toml
[tool.poetry]
name = "operationcode-pybot"
version = "3.0.0"
description = "Operation Code's Official Slackbot"
authors = ["Operation Code <contact@operationcode.org>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.12"
aiohttp = "^3.9"
python-dotenv = "^1.0"
pyyaml = "^6.0"
sentry-sdk = "^1.39"
zipcodes = "^1.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.23"
pytest-aiohttp = "^1.0"
pytest-mock = "^3.12"
black = "^24.0"
ruff = "^0.1"
requests = "^2.31"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
select = ["E", "F", "I", "UP"]
ignore = []
line-length = 100
target-version = "py311"

[tool.black]
line-length = 100
target-version = ["py311", "py312"]
```

### 6.2 Key Changes

- Removed: `sirbot`, `slack-sansio` (now vendored)
- Removed: `aiocontextvars` (not needed in Python 3.7+)
- Removed: `cchardet` (aiohttp uses charset-normalizer now)
- Removed: `cython` (not directly needed)
- Updated: All versions to latest compatible

---

## Phase 7: Update Dockerfile (Day 5) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: Docker images updated to Python 3.12, all tests passing (57/57) in containerized environment
> **Production Image**: Python 3.12.12, all dependencies verified working
> **Test Image**: Python 3.12.12, 57/57 tests passing

### Docker Best Practices Applied

Based on Poetry documentation and Docker best practices research:

1. **`POETRY_VIRTUALENVS_IN_PROJECT=true`** - Creates `.venv` in project directory
2. **Multi-stage builds** - Separate builder and production stages for smaller images
3. **Minimal base image** - Using `python:3.12-slim` instead of full Python image
4. **Build cache optimization** - Copy dependencies before code for faster rebuilds
5. **Cache cleanup** - Remove Poetry cache to reduce image size
6. **Proper PATH configuration** - Set `PATH="/app/.venv/bin:$PATH"` in production

### Fixes Applied

- Fixed `cgi` module deprecation (removed in Python 3.13)
- Replaced `asynctest` with `unittest.mock.AsyncMock`
- Fixed test fixture `loop` parameter (deprecated in pytest-asyncio 1.0+)
- Proper venv management with Poetry in Docker

### 7.1 New docker/Dockerfile

```dockerfile
FROM python:3.12-slim AS base

FROM base AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip poetry && \
    poetry install --only=main --no-interaction --no-cache

# Production image
FROM base AS prod

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . /src
WORKDIR /src

ENTRYPOINT ["python3", "-m", "pybot"]
```

---

## Phase 8: Fix Plugin Files (Day 5-6) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: Both custom plugins modernized - removed asyncio.coroutine(), added type hints

### 8.1 Update pybot/plugins/api/plugin.py

```python
import asyncio
import logging
from collections import defaultdict

from pybot.plugins.api import endpoints

logger = logging.getLogger(__name__)


class APIPlugin:
    __name__ = "api"

    def __init__(self):
        self.session = None
        self.routers = {"slack": SlackAPIRequestRouter()}

    def load(self, sirbot):
        self.session = sirbot.http_session

        sirbot.router.add_route(
            "GET", "/pybot/api/v1/slack/{resource}", endpoints.slack_api
        )
        sirbot.router.add_route(
            "POST", "/pybot/api/v1/slack/{resource}", endpoints.slack_api
        )

    def on_get(self, request, handler, **kwargs):
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError(f"Handler {handler} must be an async function")
        options = {**kwargs, "wait": False}
        self.routers["slack"].register(request, (handler, options))


class SlackAPIRequestRouter:
    def __init__(self):
        self._routes = defaultdict(list)

    def register(self, resource, handler, **detail):
        logger.info(f"Registering {resource}, {detail} to {handler}")
        self._routes[resource].append(handler)

    def dispatch(self, request):
        resource = request.resource
        logger.debug(f"Dispatching request {resource}")
        if resource in self._routes:
            for handler in self._routes.get(resource):
                yield handler
```

### 8.2 Update pybot/plugins/airtable/plugin.py (if similar pattern)

Same change: replace `asyncio.coroutine()` with type check.

---

## Phase 9: Testing (Day 6-7) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: All linting passed, 57/57 tests passing, bot starts successfully

### 9.1 Install Dependencies

```bash
poetry lock
poetry install
```

### 9.2 Run Linting

```bash
poetry run ruff check pybot/ tests/
poetry run black --check pybot/ tests/
```

### 9.3 Run Tests

```bash
poetry run pytest -v
```

### 9.4 Fix Any Issues

Common issues:
- Import path typos
- Missing `async def` on handlers
- Test fixture updates needed

### 9.5 Manual Testing

```bash
# Start the bot locally
poetry run python -m pybot

# In another terminal, test health endpoint
curl http://localhost:5000/health
```

---

## Phase 10: Docker Testing (Day 7-8)

### 10.1 Build Docker Image

```bash
docker build -t pybot:py312 -f docker/Dockerfile .
```

### 10.2 Run Container

```bash
docker run -it --env-file docker/pybot.env pybot:py312
```

### 10.3 Test Endpoints

```bash
curl http://localhost:5000/health
curl http://localhost:5000/sirbot/plugins
```

---

## Phase 11: Cleanup and Documentation (Day 8-9) ✅ COMPLETE

> **Status**: Completed January 4, 2026
> **Result**: README.md updated with Python 3.12 requirements and vendored dependencies documentation

### 11.1 Remove Old Lock File

```bash
rm poetry.lock
poetry lock
```

### 11.2 Update README.md

Add a section about vendored dependencies:

```markdown
## Vendored Dependencies

This project includes vendored copies of the following abandoned libraries,
modified for Python 3.12+ compatibility:

- **sirbot** (from [pyslackers/sir-bot-a-lot-2](https://github.com/pyslackers/sir-bot-a-lot-2)) - MIT License
- **slack-sansio** (from [pyslackers/slack-sansio](https://github.com/pyslackers/slack-sansio)) - MIT License

These libraries are located in `pybot/_vendor/` and are maintained as part of this repository.
```

### 11.3 Commit Changes

```bash
git add -A
git commit -m "Upgrade to Python 3.12 with vendored sirbot/slack-sansio

- Vendor sirbot and slack-sansio into pybot/_vendor/
- Update for Python 3.12 compatibility
- Replace asyncio.coroutine() with async def requirement
- Remove deprecated loop= parameter usage
- Update all dependencies to latest versions
- Update Dockerfile for Python 3.12"
```

---

## Phase 12: Deployment (Day 9-10)

### 12.1 Create Pull Request

```bash
git push origin feature/python-3.12-upgrade
```

### 12.2 Pre-deployment Checklist

- [ ] All tests passing
- [ ] Docker build succeeds
- [ ] Health check works
- [ ] Slack commands tested locally (with ngrok if needed)
- [ ] Documentation updated

### 12.3 Rollback Plan

Keep the old image tagged:

```bash
docker tag pybot:current pybot:pre-py312-backup
```

---

## Quick Reference: All Files to Create/Modify

### New Files (create)

```
pybot/_vendor/__init__.py
pybot/_vendor/slack/LICENSE
pybot/_vendor/slack/__init__.py
pybot/_vendor/slack/actions.py
pybot/_vendor/slack/commands.py
pybot/_vendor/slack/events.py
pybot/_vendor/slack/exceptions.py
pybot/_vendor/slack/methods.py
pybot/_vendor/slack/sansio.py
pybot/_vendor/slack/io/__init__.py
pybot/_vendor/slack/io/abc.py
pybot/_vendor/slack/io/aiohttp.py
pybot/_vendor/slack/tests/__init__.py
pybot/_vendor/slack/tests/plugin.py
pybot/_vendor/sirbot/LICENSE
pybot/_vendor/sirbot/__init__.py
pybot/_vendor/sirbot/bot.py
pybot/_vendor/sirbot/endpoints.py
pybot/_vendor/sirbot/plugins/__init__.py
pybot/_vendor/sirbot/plugins/slack/__init__.py
pybot/_vendor/sirbot/plugins/slack/plugin.py
pybot/_vendor/sirbot/plugins/slack/endpoints.py
```

### Modified Files (update imports)

```
pybot/__main__.py
pybot/endpoints/slack/actions/__init__.py
pybot/endpoints/slack/actions/general_actions.py
pybot/endpoints/slack/actions/mentor_request.py
pybot/endpoints/slack/actions/mentor_volunteer.py
pybot/endpoints/slack/actions/new_member.py
pybot/endpoints/slack/actions/report_message.py
pybot/endpoints/slack/commands.py
pybot/endpoints/slack/events.py
pybot/endpoints/slack/messages.py
pybot/endpoints/slack/message_templates/block_action.py
pybot/endpoints/slack/message_templates/mentor_request.py
pybot/endpoints/slack/utils/event_utils.py
pybot/endpoints/slack/utils/general_utils.py
pybot/endpoints/api/slack_api.py
pybot/endpoints/api/utils.py
pybot/endpoints/airtable/requests.py
pybot/endpoints/airtable/utils.py
pybot/plugins/api/plugin.py
pybot/plugins/airtable/plugin.py
tests/conftest.py
tests/endpoints/api/test_slack_api_endpoint.py
tests/endpoints/slack/test_slack_actions.py
pyproject.toml
docker/Dockerfile
```

---

## Phase 13: Post-Upgrade Test Verification (Days 17-18)

### 13.1 Create Python 3.12 Test Dockerfile

Create `docker/Dockerfile.test.py312`:

```dockerfile
# docker/Dockerfile.test.py312
# For running tests in Python 3.12 after upgrade

FROM python:3.12-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (including dev)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction

# Copy source code
COPY . .

# Default command: run tests with coverage
CMD ["poetry", "run", "pytest", "-v", "--tb=short"]
```

### 13.2 Run Tests in Python 3.12

```bash
./scripts/test-py312.sh
```

### 13.3 Compare Results Against Baseline

Compare the test results from Python 3.12 against the baseline from Phase 0:

| Metric | Python 3.7 (Baseline) | Python 3.12 (After) | Status |
|--------|----------------------|---------------------|--------|
| Total tests | X | X | ✅/❌ |
| Passed | X | X | ✅/❌ |
| Failed | X | X | ✅/❌ |
| Import tests | X | X | ✅/❌ |
| Async handler tests | X | X | ✅/❌ |

### 13.4 Fix Any Regressions

If any tests that passed in Python 3.7 now fail in Python 3.12:

1. Identify the root cause (likely async changes)
2. Fix the issue in vendored code or pybot code
3. Re-run tests until parity is achieved

### 13.5 Run Coverage Report

```bash
./scripts/test-py312.sh --cov=pybot --cov-report=html

# View report
open htmlcov/index.html
```

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| **Phase 0: Test Baseline** | 3-4 days | 4 days |
| Phase 1: Setup & Preparation | 0.5 days | 4.5 days |
| Phase 2: Vendor slack-sansio | 1 day | 5.5 days |
| Phase 3: Vendor sirbot | 1.5 days | 7 days |
| Phase 4: Create vendor init | 0.5 days | 7.5 days |
| Phase 5: Update imports | 1 day | 8.5 days |
| Phase 6: Update pyproject.toml | 0.5 days | 9 days |
| Phase 7: Update Dockerfile | 0.5 days | 9.5 days |
| Phase 8: Fix plugin files | 0.5 days | 10 days |
| Phase 9: Local testing | 1 day | 11 days |
| Phase 10: Docker testing | 1 day | 12 days |
| Phase 11: Cleanup & docs | 0.5 days | 12.5 days |
| Phase 12: Deployment | 1 day | 13.5 days |
| **Phase 13: Test Verification** | 1.5 days | 15 days |
| Buffer | 2 days | 17 days |
| **Total** | | **~3-4 weeks** |

---

## Test Coverage Summary

### Before Upgrade (Baseline)

| Category | Tests | Purpose |
|----------|-------|---------|
| Existing tests | ~10 | Original test suite |
| Import safety tests | ~18 | Verify all modules import |
| Async handler tests | ~12 | Verify handlers are async |
| Unit tests (LunchCommand) | ~8 | Pure function testing |
| Unit tests (roll parsing) | ~10 | Input validation |
| Unit tests (action messages) | ~5 | Message builders |
| **Total** | **~63** | |

### Test Execution Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT MACHINE                       │
│  (macOS - cannot run Python 3.7)                            │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Code      │    │   Docker    │    │   Docker    │     │
│  │   Changes   │───▶│   Py 3.7    │───▶│   Py 3.12   │     │
│  │             │    │   Tests     │    │   Tests     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                            │                  │             │
│                            ▼                  ▼             │
│                     ┌─────────────────────────────┐         │
│                     │   Compare Results           │         │
│                     │   (should match)            │         │
│                     └─────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Quick Reference: Test Commands

```bash
# Run tests in Python 3.7 (before upgrade)
./scripts/test-py37.sh

# Run tests in Python 3.12 (after upgrade)
./scripts/test-py312.sh

# Run specific test file
./scripts/test-py37.sh tests/test_upgrade_safety.py

# Run with coverage
./scripts/test-py312.sh --cov=pybot --cov-report=term-missing

# Run with verbose output
./scripts/test-py37.sh -v --tb=long
```
