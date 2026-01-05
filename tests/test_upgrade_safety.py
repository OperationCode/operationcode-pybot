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
