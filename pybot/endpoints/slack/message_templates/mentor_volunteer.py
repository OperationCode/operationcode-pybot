from collections.abc import MutableMapping
from enum import IntEnum

from pybot.endpoints.slack.utils import MENTOR_CHANNEL

from .block_action import BlockAction


class VolunteerBlockIndex(IntEnum):
    SKILLSET_OPTIONS = 2
    SELECTED_SKILLSETS = 3
    SUBMIT = 5


class MentorVolunteer(BlockAction):
    def __init__(self, raw_action: MutableMapping):
        super().__init__(raw_action)

        if "original_message" not in self:
            self["original_message"] = {}

    @property
    def skillsets(self) -> [str]:
        skillset_field = self.skillset_field_text
        return skillset_field.split("\n")

    @property
    def skillset_field_text(self) -> str:
        return self.blocks[VolunteerBlockIndex.SELECTED_SKILLSETS]["fields"][0]["text"]

    @skillset_field_text.setter
    def skillset_field_text(self, value):
        self.blocks[VolunteerBlockIndex.SELECTED_SKILLSETS]["fields"][0]["text"] = value

    def add_skillset(self, skillset: str) -> None:
        """
        Appends the new skillset to the displayed skillsets
        """
        if skillset not in self.skillsets:
            self.skillset_field_text += f"\n{skillset}"

    def clear_skillsets(self) -> None:
        self.skillset_field_text = " "

    def validate_self(self):
        if not self.skillsets:
            return False

        self.clear_errors()
        return True

    def add_errors(self) -> None:
        submit_attachment = {
            "text": ":warning: Please select at least one area. :warning:",
            "color": "danger",
        }
        self.attachments = [submit_attachment]

    def airtable_error(self, airtable_response) -> None:
        error_attachment = {
            "text": (
                f"Something went wrong.\n"
                f"Error Type:{airtable_response['error']['type']}\n"
                f"Error Message: {airtable_response['error']['message']}"
            ),
            "color": "danger",
        }
        self.attachments = [error_attachment]

    def on_submit_success(self):
        done_blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": success_message}},
            {
                "type": "actions",
                "block_id": "submission",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "cancel_btn",
                        "text": {"type": "plain_text", "text": "Dismiss"},
                        "value": "dismiss",
                    }
                ],
            },
        ]
        self.blocks = done_blocks


success_message = (
    "Thank you for signing up to be a mentor for Operation Code! You should have been automatically "
    f"added to the <#{MENTOR_CHANNEL}|mentors-internal> channel. There is a bot that posts in that "
    "channel when someone signs up for a 30 minute session with a mentor. If the skillsets they request "
    "match the ones you listed when you signed up, you'll be notified in the thread. Click the green "
    "button to claim them and reach out via DM to schedule a slack call. There are also a few pinned "
    f"items in that channel that may be helpful. If you have any questions, please DM <@Raz0r|Raz0r>.\n\n"
    "We don't currently have a formal long term mentorship program, but if you feel like continuing to "
    "keep in contact with any members you speak to, that's perfectly fine.\n\n"
    "Thank you for signing up!"
)
