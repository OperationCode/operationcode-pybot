from enum import IntEnum
from typing import Any, Coroutine, MutableMapping, Optional

from slack import methods
from slack.actions import Action
from slack.io.abc import SlackAPI

from pybot.endpoints.slack.utils.action_messages import now
from pybot.plugins.airtable.api import AirtableAPI


class BlockIndex(IntEnum):
    SERVICE = 2
    SKILLSET = 3
    SELECTED_SKILLSETS = 4
    MENTOR = 5
    COMMENTS = 6
    AFFILIATION = 7
    SUBMIT = 9


class MentorRequest(Action):
    def __init__(self, raw_action: MutableMapping):
        super().__init__(raw_action)

        if "original_message" not in self:
            self["original_message"] = {}

    @property
    def channel(self):
        return self["channel"]["id"]

    @property
    def original_message(self):
        return self["message"]

    @property
    def blocks(self):
        return self.original_message["blocks"]

    @blocks.setter
    def blocks(self, value):
        self.original_message["blocks"] = value

    @property
    def attachments(self):
        return self.original_message.get("attachments", [])

    @attachments.setter
    def attachments(self, value):
        self.original_message["attachments"] = value

    @property
    def ts(self):
        return self.original_message["ts"]

    @property
    def actions(self):
        return self["actions"]

    @property
    def selected_option(self):
        if "selected_option" in self.actions[0]:
            return self.actions[0]["selected_option"]
        return None

    def initial_option(self, index: BlockIndex) -> str:
        """
        Each section uses the `initial_option` key to store the latest
        option selected by the user
        """
        accessory = self.blocks[index]["accessory"]
        if "initial_option" in accessory:
            return accessory["initial_option"]["value"]
        return ""

    @property
    def service(self):
        return self.initial_option(BlockIndex.SERVICE)

    @service.setter
    def service(self, new_service):
        block = self.blocks[BlockIndex.SERVICE]
        block["accessory"]["initial_option"] = new_service
        if self.validate_self():
            self.clear_errors()

    @property
    def skillsets(self) -> [str]:
        if self.skillset_fields:
            return [field["text"] for field in self.skillset_fields]
        return []

    @property
    def skillset_fields(self) -> list:
        return self.blocks[BlockIndex.SELECTED_SKILLSETS].get("fields", [])

    def add_skillset(self, skillset: str) -> None:
        """
        Appends the new skillset to the displayed skillsets
        """
        if skillset not in self.skillsets:
            new_field = {"type": "plain_text", "text": skillset, "emoji": True}
            self.blocks[BlockIndex.SELECTED_SKILLSETS].setdefault("fields", []).append(
                new_field
            )

    @property
    def mentor(self) -> Optional[str]:
        option = self.initial_option(BlockIndex.MENTOR)
        if option == "None":
            return None
        return option

    @mentor.setter
    def mentor(self, new_mentor: str) -> None:
        self.blocks[BlockIndex.MENTOR]["accessory"]["initial_option"] = new_mentor

    @property
    def details(self) -> str:
        block = self.blocks[BlockIndex.COMMENTS]
        if "fields" in block:
            return block["fields"][0]["text"]
        return ""

    @details.setter
    def details(self, new_details: str) -> None:
        field = {"type": "plain_text", "text": new_details}
        self.blocks[BlockIndex.COMMENTS]["fields"] = [field]

    @property
    def affiliation(self) -> str:
        return self.initial_option(BlockIndex.AFFILIATION)

    @affiliation.setter
    def affiliation(self, new_affiliation: str) -> None:
        self.blocks[BlockIndex.AFFILIATION]["accessory"][
            "initial_option"
        ] = new_affiliation

        if self.validate_self():
            self.clear_errors()

    @property
    def update_params(self) -> dict:
        return {
            "channel": self.channel,
            "ts": self.ts,
            "blocks": self.blocks,
            "attachments": self.attachments,
        }

    def validate_self(self) -> bool:
        if not self.service or not self.affiliation:
            return False
        self.clear_errors()
        return True

    def add_errors(self) -> None:
        submit_attachment = {
            "text": ":warning: Service and group certification are required. :warning:",
            "color": "danger",
        }
        self.attachments = [submit_attachment]

    async def submit_request(self, username: str, email: str, airtable: AirtableAPI):
        params = {"Slack User": username, "Email": email, "Status": "Available"}
        if self.skillsets:
            params["Skillsets"] = self.skillsets
        if self.details:
            params["Additional Details"] = self.details
        if self.mentor:
            mentor_records = await airtable.find_records(
                "Mentors", "Full Name", self.mentor
            )
            params["Mentor Requested"] = [mentor_records[0]["id"]]

        service_records = await airtable.find_records("Services", "Name", self.service)
        params["Service"] = [service_records[0]["id"]]
        return await airtable.add_record("Mentor Request", {"fields": params})

    def submission_error(
        self, airtable_response, slack: SlackAPI
    ) -> Coroutine[Any, Any, dict]:
        error_attachment = {
            "text": (
                f"Something went wrong.\n"
                f'Error Type:{airtable_response["error"]["type"]}\n'
                f'Error Message: {airtable_response["error"]["message"]}'
            ),
            "color": "danger",
        }
        self.attachments = [error_attachment]
        return self.update_message(slack)

    def submission_complete(self, slack: SlackAPI) -> Coroutine[Any, Any, dict]:
        done_block = {
            "type": "section",
            "block_id": "submission",
            "text": {"type": "mrkdwn", "text": "Request Submitted Successfully!"},
            "accessory": {
                "type": "button",
                "action_id": "cancel_btn",
                "text": {"type": "plain_text", "text": "Dimiss", "emoji": True},
                "value": "dismiss",
            },
        }

        self.blocks = [done_block]

        return self.update_message(slack)

    def clear_skillsets(self) -> None:
        if self.skillset_fields:
            del self.blocks[BlockIndex.SELECTED_SKILLSETS]["fields"]

    def clear_errors(self) -> None:
        self.attachments = []

    async def delete_self(self, slack: SlackAPI) -> None:
        params = {"ts": self.ts, "channel": self.channel}
        await slack.query(methods.CHAT_DELETE, params)

    def update_message(self, slack: SlackAPI) -> Coroutine[Any, Any, dict]:
        return slack.query(methods.CHAT_UPDATE, self.update_params)


class MentorRequestClaim(Action):
    def __init__(
        self, raw_action: MutableMapping, slack: SlackAPI, airtable: AirtableAPI
    ):
        super().__init__(raw_action)
        self.slack = slack
        self.airtable = airtable
        self.text = raw_action["original_message"]["text"]
        self.attachment = raw_action["original_message"]["attachments"][0]
        self.should_update = True

    @property
    def trigger(self) -> dict:
        return self["actions"][0]

    @property
    def click_type(self) -> str:
        """
        Value of the button clicked.
        """
        return self.trigger["value"]

    def is_claim(self) -> bool:
        """
        Returns true if the Claim button was clicked
        """
        return self.click_type == "mentee_claimed"

    @property
    def record(self) -> str:
        """
        Airtable record ID for the mentor request
        """
        return self.trigger["name"]

    @property
    def clicker(self) -> str:
        """
        The Slack User ID of the button clicker
        """
        return self["user"]["id"]

    @property
    def attachment(self) -> dict:
        return self["original_message"]["attachments"][0]

    @attachment.setter
    def attachment(self, value: dict) -> None:
        self["original_message"]["attachments"][0] = value

    def claim_request(self, mentor_record):
        """
        Updates the airtable entry with the given record.

        If record couldn't be found this object's text field is changed
        to an error message to be displayed when update_message is called
        """
        if mentor_record:
            self.attachment = self.mentee_claimed_attachment()
        else:
            self.attachment[
                "text"
            ] = f":warning: <@{self.clicker}>'s slack Email not found in Mentor table. :warning:"
            self.should_update = False

        return self.update_airtable(mentor_record)

    def unclaim_request(self):
        """
        Changes the attachment to the un-claimed version and deletes the mentor from the
        Airtable record
        """
        self.attachment = self.mentee_unclaimed_attachment()
        return self.update_airtable("")

    async def update_airtable(self, mentor_id: Optional[str]):
        if mentor_id is not None:
            return await self.airtable.update_request(self.record, mentor_id)

    async def update_message(self):
        """
        Builds the slack API call to update the original message
        """
        response = {
            "channel": self["channel"]["id"],
            "ts": self["message_ts"],
            "text": self.text,
            "attachments": self["original_message"]["attachments"],
        }
        await self.slack.query(methods.CHAT_UPDATE, response)

    def mentee_claimed_attachment(self) -> dict:
        return {
            "text": f":100: Request claimed by <@{self.clicker}>:100:\n"
            f"<!date^{now()}^Claimed at {{date_num}} {{time_secs}}|Failed to parse time>",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "claim_mentee",
            "attachment_type": "default",
            "actions": [
                {
                    "name": f"{self.record}",
                    "text": f"Reset claim",
                    "type": "button",
                    "style": "danger",
                    "value": "reset_claim_mentee",
                }
            ],
        }

    def mentee_unclaimed_attachment(self) -> dict:
        return {
            "text": f"Reset by <@{self.clicker}> at"
            f" <!date^{now()}^ {{date_num}} {{time_secs}}|Failed to parse time>",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "claim_mentee",
            "attachment_type": "default",
            "actions": [
                {
                    "name": f"{self.record}",
                    "text": "Claim Mentee",
                    "type": "button",
                    "style": "primary",
                    "value": "mentee_claimed",
                }
            ],
        }
