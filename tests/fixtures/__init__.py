"""
Reusable mock classes for testing Slack and Airtable integrations.
"""

from unittest.mock import AsyncMock, MagicMock
from typing import Any


class SlackMock:
    """
    Mock wrapper for Slack API interactions.

    Wraps bot["plugins"]["slack"].api.query to provide easy setup
    of user info, method responses, and assertions.
    """

    def __init__(self, bot):
        self.bot = bot
        self.query_mock = AsyncMock()
        self._user_info_responses: dict[str, dict] = {}
        self._method_responses: dict[str, Any] = {}
        self._error_responses: dict[str, Exception] = {}
        self._call_history: list[tuple[str, dict]] = []
        self._email_lookup: dict[str, str] = {}

        # Set up the mock
        self.query_mock.side_effect = self._handle_query
        bot["plugins"]["slack"].api.query = self.query_mock

    async def _handle_query(self, method: str = "", data: dict | None = None, **kwargs) -> dict:
        """Handle incoming Slack API queries."""
        # Method can be passed as first arg or as url= kwarg
        actual_method = kwargs.get("url", method)

        # Extract URL from Methods enum (the value is a namedtuple with url attribute)
        if hasattr(actual_method, 'value') and hasattr(actual_method.value, 'url'):
            method_url = actual_method.value.url
        elif hasattr(actual_method, 'url'):
            method_url = actual_method.url
        elif isinstance(actual_method, str):
            method_url = actual_method
        else:
            # Fallback - store the method object itself (will be stringified later)
            method_url = actual_method

        self._call_history.append((method_url, data or {}))

        # Check for error responses first
        if method_url in self._error_responses:
            raise self._error_responses[method_url]

        # Ensure method_url is a string for substring checks
        method_str = str(method_url) if method_url else ""

        # Check for users.lookupByEmail requests
        if "lookupByEmail" in method_str and data and "email" in data:
            email = data["email"]
            if email in self._email_lookup:
                return {"ok": True, "user": {"id": self._email_lookup[email]}}
            # Raise error if email not found
            from pybot._vendor.slack.exceptions import SlackAPIError
            raise SlackAPIError(error={"ok": False, "error": "users_not_found"}, headers={}, data={})

        # Check for user.info requests
        if "users.info" in method_str and data and "user" in data:
            user_id = data["user"]
            if user_id in self._user_info_responses:
                return self._user_info_responses[user_id]

        # Check for method-specific responses (use original method_url for dict lookup)
        if method_url in self._method_responses:
            response = self._method_responses[method_url]
            if callable(response):
                return response(data)
            return response

        # Also check using method_str for string-based lookups
        if method_str in self._method_responses:
            response = self._method_responses[method_str]
            if callable(response):
                return response(data)
            return response

        # Check for partial URL matches (e.g., "chat.postMessage" matches "https://slack.com/api/chat.postMessage")
        for key, response in self._method_responses.items():
            if isinstance(key, str) and key in method_str:
                if callable(response):
                    return response(data)
                return response

        # Default response - add 'ts' for chat methods
        default_response = {"ok": True}
        if "chat.post" in method_str.lower() or "chat.update" in method_str.lower():
            default_response["ts"] = "1234567890.123456"
        return default_response

    def setup_user_info(self, user_id: str, email: str | None = None,
                       name: str = "Test User", real_name: str = "Test User") -> "SlackMock":
        """Configure response for users.info API call."""
        profile = {"real_name": real_name}
        if email:
            profile["email"] = email

        self._user_info_responses[user_id] = {
            "ok": True,
            "user": {
                "id": user_id,
                "name": name,
                "real_name": real_name,
                "profile": profile,
            }
        }
        return self

    def setup_method_response(self, method: str, response: Any) -> "SlackMock":
        """Configure response for a specific Slack API method."""
        self._method_responses[method] = response
        return self

    def setup_error_response(self, method: str, error: Exception) -> "SlackMock":
        """Configure an error to be raised for a specific method."""
        self._error_responses[method] = error
        return self

    def setup_lookup_by_email(self, email: str, user_id: str) -> "SlackMock":
        """Configure users.lookupByEmail response."""
        self._email_lookup[email] = user_id
        return self

    def assert_called_with_method(self, method: str, times: int | None = None) -> None:
        """Assert a Slack API method was called a specific number of times."""
        call_count = sum(1 for m, _ in self._call_history if method in str(m))
        if times is not None:
            assert call_count == times, f"Expected {method} to be called {times} times, got {call_count}"
        else:
            assert call_count > 0, f"Expected {method} to be called at least once"

    def assert_message_sent_to_channel(self, channel_id: str, text_contains: str | None = None) -> None:
        """Assert a message was sent to a specific channel."""
        for method, data in self._call_history:
            if "chat" in method and data.get("channel") == channel_id:
                if text_contains is None:
                    return
                if text_contains in data.get("text", ""):
                    return
        raise AssertionError(
            f"No message found for channel {channel_id}" +
            (f" containing '{text_contains}'" if text_contains else "")
        )

    def get_calls(self, method: str | None = None) -> list[tuple[str, dict]]:
        """Get all calls, optionally filtered by method."""
        if method is None:
            return self._call_history
        return [(m, d) for m, d in self._call_history if method in str(m)]

    def reset(self) -> None:
        """Reset all call history and responses."""
        self._call_history.clear()
        self._user_info_responses.clear()
        self._method_responses.clear()
        self._error_responses.clear()


class AirtableMock:
    """
    Mock wrapper for Airtable API interactions.

    Wraps bot["plugins"]["airtable"].api methods to provide easy setup
    of service records, mentor records, and assertions.
    """

    def __init__(self, bot):
        self.bot = bot
        self.api = bot["plugins"]["airtable"].api

        self._services: dict[str, dict] = {}
        self._mentors: dict[str, dict] = {}
        self._records: dict[str, list[dict]] = {}
        self._errors: dict[tuple[str, str], Exception] = {}
        self._add_record_history: list[tuple[str, dict]] = []
        self._update_history: list[tuple[str, str]] = []

        # Set up the mocks
        self._setup_mocks()

    def _setup_mocks(self):
        """Configure all the mock methods."""
        self.api.find_records = AsyncMock(side_effect=self._handle_find_records)
        self.api.add_record = AsyncMock(side_effect=self._handle_add_record)
        self.api.update_request = AsyncMock(side_effect=self._handle_update_request)
        self.api.get_name_from_record_id = AsyncMock(side_effect=self._handle_get_name)
        self.api.get_row_from_record_id = AsyncMock(side_effect=self._handle_get_row)
        self.api.find_mentors_with_matching_skillsets = AsyncMock(
            side_effect=self._handle_find_mentors
        )
        self.api.get_all_records = AsyncMock(side_effect=self._handle_get_all_records)

    async def _handle_find_records(self, table_name: str, field: str, value: str) -> list[dict]:
        """Handle find_records calls."""
        error_key = (table_name, "find")
        if error_key in self._errors:
            raise self._errors[error_key]

        if table_name == "Services":
            for service_id, service in self._services.items():
                if service.get("Name") == value:
                    return [{"id": service_id, "fields": service}]
            return []

        if table_name == "Mentors":
            results = []
            for mentor_id, mentor in self._mentors.items():
                if mentor.get(field) == value:
                    results.append({"id": mentor_id, "fields": mentor})
            return results

        # Check generic records
        if table_name in self._records:
            return [r for r in self._records[table_name] if r.get("fields", {}).get(field) == value]

        return []

    async def _handle_add_record(self, table: str, data: dict) -> dict:
        """Handle add_record calls."""
        self._add_record_history.append((table, data))

        error_key = (table, "add")
        if error_key in self._errors:
            return {"error": {"type": "MOCK_ERROR", "message": str(self._errors[error_key])}}

        return {"id": f"rec{len(self._add_record_history)}", **data}

    async def _handle_update_request(self, record_id: str, mentor_id: str) -> dict:
        """Handle update_request calls."""
        self._update_history.append((record_id, mentor_id))
        return {"ok": True}

    async def _handle_get_name(self, table: str, record_id: str) -> str | None:
        """Handle get_name_from_record_id calls."""
        if table == "Services" and record_id in self._services:
            return self._services[record_id].get("Name")
        if table == "Mentors" and record_id in self._mentors:
            return self._mentors[record_id].get("Name")
        return None

    async def _handle_get_row(self, table: str, record_id: str) -> dict:
        """Handle get_row_from_record_id calls."""
        if table == "Mentors" and record_id in self._mentors:
            return self._mentors[record_id]
        if table == "Services" and record_id in self._services:
            return self._services[record_id]
        return {}

    async def _handle_find_mentors(self, skillsets: str) -> list[dict]:
        """Handle find_mentors_with_matching_skillsets calls."""
        if not skillsets:
            return []

        results = []
        requested_skillsets = set(s.strip() for s in skillsets.split(","))

        for mentor in self._mentors.values():
            mentor_skillsets = set(mentor.get("Skillsets", []))
            if mentor_skillsets & requested_skillsets:
                results.append(mentor)

        return results

    async def _handle_get_all_records(self, table: str, field: str) -> list[str]:
        """Handle get_all_records calls."""
        if table == "Services":
            return [s.get(field) for s in self._services.values() if s.get(field)]
        if table == "Mentors":
            return [m.get(field) for m in self._mentors.values() if m.get(field)]
        return []

    def setup_service(self, name: str, record_id: str | None = None) -> "AirtableMock":
        """Add a service to the mock."""
        record_id = record_id or f"recsvc{len(self._services)}"
        self._services[record_id] = {"Name": name}
        return self

    def setup_mentor(self, name: str, email: str, skillsets: list[str] | None = None,
                    record_id: str | None = None, slack_name: str | None = None) -> "AirtableMock":
        """Add a mentor to the mock."""
        record_id = record_id or f"recmentor{len(self._mentors)}"
        self._mentors[record_id] = {
            "Name": name,
            "Email": email,
            "Skillsets": skillsets or [],
            "Slack Name": slack_name or name.lower().replace(" ", ""),
        }
        return self

    def setup_error(self, table: str, operation: str, error: Exception | str) -> "AirtableMock":
        """Configure an error for a specific table/operation combination."""
        if isinstance(error, str):
            error = Exception(error)
        self._errors[(table, operation)] = error
        return self

    def assert_record_added(self, table: str, fields_contain: dict | None = None) -> None:
        """Assert a record was added to a table."""
        matching = [t for t, d in self._add_record_history if t == table]
        assert matching, f"No records added to {table}"

        if fields_contain:
            for _, data in self._add_record_history:
                fields = data.get("fields", {})
                if all(fields.get(k) == v for k, v in fields_contain.items()):
                    return
            raise AssertionError(f"No record with fields {fields_contain} added to {table}")

    def assert_mentor_assigned(self, request_record: str) -> None:
        """Assert a mentor was assigned to a request."""
        for record_id, mentor_id in self._update_history:
            if record_id == request_record and mentor_id:
                return
        raise AssertionError(f"No mentor assigned to request {request_record}")

    def get_added_records(self, table: str | None = None) -> list[tuple[str, dict]]:
        """Get all added records, optionally filtered by table."""
        if table is None:
            return self._add_record_history
        return [(t, d) for t, d in self._add_record_history if t == table]

    def reset(self) -> None:
        """Reset call history (but keep service/mentor setup)."""
        self._add_record_history.clear()
        self._update_history.clear()


class AdminSlackMock:
    """Mock for admin_slack plugin used for channel invites."""

    def __init__(self, bot):
        self.bot = bot
        self.query_mock = AsyncMock(return_value={"ok": True})
        self._invite_history: list[tuple[str, list[str]]] = []
        self._errors: dict[str, Exception] = {}

        # Create a mock admin_slack plugin if it doesn't exist
        if "admin_slack" not in bot["plugins"]:
            from unittest.mock import MagicMock
            bot["plugins"]["admin_slack"] = MagicMock()
            bot["plugins"]["admin_slack"].api = MagicMock()

        self.query_mock.side_effect = self._handle_query
        bot["plugins"]["admin_slack"].api.query = self.query_mock

    async def _handle_query(self, method: str, data: dict | None = None, **kwargs) -> dict:
        """Handle admin Slack API queries."""
        # Extract URL from Methods enum if needed
        if hasattr(method, 'value') and hasattr(method.value, 'url'):
            method_url = method.value.url
        elif isinstance(method, str):
            method_url = method
        else:
            method_url = str(method)

        if "conversations.invite" in method_url and data:
            channel = data.get("channel")
            users = data.get("users", [])
            self._invite_history.append((channel, users))

            if method_url in self._errors:
                raise self._errors[method_url]

        return {"ok": True}

    def setup_invite_error(self, error: Exception) -> "AdminSlackMock":
        """Configure an error for channel invites."""
        from pybot._vendor.slack import methods
        self._errors[methods.CONVERSATIONS_INVITE.value.url] = error
        return self

    def assert_invited_to_channel(self, channel: str, user_id: str | None = None) -> None:
        """Assert a user was invited to a channel."""
        for ch, users in self._invite_history:
            if ch == channel:
                if user_id is None or user_id in users:
                    return
        raise AssertionError(
            f"No invite found for channel {channel}" +
            (f" with user {user_id}" if user_id else "")
        )

    def reset(self) -> None:
        """Reset invite history."""
        self._invite_history.clear()
