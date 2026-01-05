from __future__ import annotations

from enum import IntEnum
from typing import Any, Coroutine, MutableMapping, Optional

from pybot._vendor.slack import methods
from pybot._vendor.slack.actions import Action
from pybot._vendor.slack.io.abc import SlackAPI


class BlockAction(Action):
    """
    Base class for working with Block format Slack Action events.
    See https://api.slack.com/reference/messaging/blocks
    and https://api.slack.com/messaging/composing/layouts
    """

    def __init__(self, raw_action: MutableMapping):
        super().__init__(raw_action)

    @property
    def original_message(self):
        return self["message"]

    @property
    def channel(self):
        return self["channel"]["id"]

    @property
    def blocks(self) -> list:
        return self.original_message["blocks"]

    @blocks.setter
    def blocks(self, value) -> None:
        self.original_message["blocks"] = value

    @property
    def attachments(self) -> list:
        return self.original_message.get("attachments", [])

    @attachments.setter
    def attachments(self, value) -> None:
        self.original_message["attachments"] = value

    @property
    def ts(self) -> str:
        return self.original_message["ts"]

    @property
    def actions(self):
        return self["actions"]

    @property
    def selected_option(self) -> Optional[dict]:
        if "selected_option" in self.actions[0]:
            return self.actions[0]["selected_option"]
        return None

    def initial_option(self, index: IntEnum) -> str:
        """
        Each section uses the `initial_option` key to store the latest
        option selected by the user
        """
        accessory = self.blocks[index]["accessory"]
        if "initial_option" in accessory:
            return accessory["initial_option"]["value"]
        return ""

    @property
    def update_params(self) -> dict:
        return {
            "channel": self.channel,
            "ts": self.ts,
            "blocks": self.blocks,
            "attachments": self.attachments,
        }

    def validate_self(self) -> bool:
        """
        Should be overridden if action has any validation
        """
        return True

    def update_message(self, slack: SlackAPI) -> Coroutine[Any, Any, dict]:
        return slack.query(methods.CHAT_UPDATE, self.update_params)

    def add_errors(self):
        error_attachment = {
            "text": ":warning: Error - Cannot submit with current values :warning:",
            "color": "danger",
        }
        self.attachments = [error_attachment]

    def clear_errors(self) -> None:
        self.attachments = []
