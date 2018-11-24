from enum import IntEnum
from typing import MutableMapping, Optional

from slack import methods
from slack.actions import Action
from slack.io.abc import SlackAPI

from pybot.endpoints.slack.utils.action_messages import now
from pybot.plugins.airtable.api import AirtableAPI


class AttachmentIndex(IntEnum):
    SERVICE = 0
    SKILLSET = 1
    MENTOR = 2
    DETAILS = 3
    GROUP = 4
    SUBMIT = 5


class MentorRequest(Action):

    def __init__(self, raw_action: MutableMapping):
        super().__init__(raw_action)
        if 'original_message' not in self:
            self['original_message'] = {}

    @property
    def channel(self):
        return self['channel']['id']

    @classmethod
    def selected_option(cls, attachment):
        action = attachment['actions'][0]
        if 'selected_options' in action:
            return action['selected_options'][0]['value']
        return ''

    @property
    def attachments(self):
        return self['original_message']['attachments']

    @attachments.setter
    def attachments(self, value):
        self['original_message']['attachments'] = value

    @property
    def service(self):
        attachment = self.attachments[AttachmentIndex.SERVICE]
        return self.selected_option(attachment)

    @service.setter
    def service(self, new_service):
        action = self.attachments[AttachmentIndex.SERVICE]['actions'][0]
        action['selected_options'] = [{'value': new_service, 'text': new_service}]
        self.attachments[AttachmentIndex.SERVICE]['color'] = ''

    @property
    def skillsets(self):
        if 'text' in self.attachments[AttachmentIndex.SKILLSET]:
            return self.attachments[AttachmentIndex.SKILLSET]['text'].split('\n')
        return []

    def add_skillset(self, skillset: str) -> None:
        """
        Appends the new skillset to the displayed skillsets
        """
        if skillset not in self.skillsets:
            skills = self.skillsets
            skills.append(skillset)
        else:
            skills = self.skillsets
        self.attachments[AttachmentIndex.SKILLSET]['text'] = '\n'.join(skills)

    @property
    def mentor(self) -> str:
        attachment = self.attachments[AttachmentIndex.MENTOR]
        return self.selected_option(attachment)

    @mentor.setter
    def mentor(self, new_mentor: str) -> None:
        action = self.attachments[AttachmentIndex.MENTOR]['actions'][0]
        action['selected_options'] = [{'value': new_mentor, 'text': new_mentor}]
        action['color'] = ''

    @property
    def certify_group(self) -> str:
        attachment = self.attachments[AttachmentIndex.GROUP]
        return self.selected_option(attachment)

    @certify_group.setter
    def certify_group(self, group: str) -> None:
        action = self.attachments[AttachmentIndex.GROUP]['actions'][0]
        action['selected_options'] = [{'value': group, 'text': group}]
        self.attachments[AttachmentIndex.GROUP]['color'] = ''

    @property
    def details(self):
        attachment = self.attachments[AttachmentIndex.DETAILS]
        if 'text' in attachment:
            return attachment['text']
        return ''

    @details.setter
    def details(self, new_details):
        self.attachments[AttachmentIndex.DETAILS]['text'] = new_details

    @property
    def update_params(self):
        return {
            'channel': self.channel,
            'ts': self['original_message'].get('ts'),
            'attachments': self.attachments
        }

    def validate_self(self):
        if not self.service or not self.certify_group:
            submit_attachment = self.attachments[AttachmentIndex.SUBMIT]
            submit_attachment['text'] = ':warning: Service and group certification are required. :warning:'
            submit_attachment['color'] = 'danger'
            if not self.service:
                self.attachments[AttachmentIndex.SERVICE]['color'] = 'danger'
            if not self.certify_group:
                self.attachments[AttachmentIndex.GROUP]['color'] = 'danger'
            return False
        return True

    async def submit_request(self, username, email, airtable: AirtableAPI):
        params = {
            'Slack User': username,
            'Email': email,
            'Status': 'Available'
        }
        if self.skillsets:
            params['Skillsets'] = self.skillsets
        if self.details:
            params['Additional Details'] = self.details
        if self.mentor:
            mentor_records = await airtable.find_records('Mentors', 'Full Name', self.mentor)
            params['Mentor Requested'] = [mentor_records[0]['id']]

        service_records = await airtable.find_records('Services', 'Name', self.service)
        params['Service'] = [service_records[0]['id']]
        return await airtable.add_record('Mentor Request', {'fields': params})

    def submission_error(self, airtable_response, slack: SlackAPI):
        self.attachments[AttachmentIndex.SUBMIT]['text'] = (
            f'Something went wrong.\n'
            f'Error Type:{airtable_response["error"]["type"]}\n'
            f'Error Message: {airtable_response["error"]["message"]}'
        )
        self.attachments[AttachmentIndex.SUBMIT]['color'] = 'danger'
        return self.update_message(slack)

    def submission_complete(self, slack: SlackAPI):
        done_attachment = self.attachments[AttachmentIndex.SUBMIT]
        done_attachment['text'] = 'Request submitted successfully!'
        done_attachment['actions'] = [{'type': 'button', 'text': 'Dismiss', 'name': 'cancel', 'value': 'cancel'}]

        self['original_message']['attachments'] = [done_attachment]
        return self.update_message(slack)

    def clear_skillsets(self):
        self.attachments[AttachmentIndex.SKILLSET]['text'] = ''

    def update_message(self, slack: SlackAPI):
        return slack.query(methods.CHAT_UPDATE, self.update_params)


class MentorRequestClaim(Action):

    def __init__(self, raw_action: MutableMapping, slack: SlackAPI, airtable: AirtableAPI):
        super().__init__(raw_action)
        self.slack = slack
        self.airtable = airtable
        self.attachment = raw_action['original_message']['attachments'][0]
        self.should_update = True

    @property
    def trigger(self) -> dict:
        return self['actions'][0]

    @property
    def click_type(self) -> str:
        """
        Value of the button clicked.
        """
        return self.trigger['value']

    def is_claim(self) -> bool:
        """
        Returns true if the Claim button was clicked
        """
        return self.click_type == 'mentee_claimed'

    @property
    def record(self) -> str:
        """
        Airtable record ID for the mentor request
        """
        return self.trigger['name']

    @property
    def clicker(self) -> str:
        """
        The Slack User ID of the button clicker
        """
        return self['user']['id']

    @property
    def attachment(self) -> dict:
        return self['original_message']['attachments'][0]

    @attachment.setter
    def attachment(self, value: dict) -> None:
        self['original_message']['attachments'][0] = value

    def claim_request(self, mentor_record):
        """
        Updates the airtable entry with the given record.

        If record couldn't be found this object's text field is changed
        to an error message to be displayed when update_message is called
        """
        if mentor_record:
            self.attachment = self.mentee_claimed_attachment()
        else:
            self.attachment['text'] = f":warning: <@{self.clicker}>'s slack Email not found in Mentor table. :warning:"
            self.should_update = False

        return self.update_airtable(mentor_record)

    def unclaim_request(self):
        """
        Changes the attachment to the un-claimed version and deletes the mentor from the
        Airtable record
        """
        self.attachment = self.mentee_unclaimed_attachment()
        return self.update_airtable('')

    async def update_airtable(self, mentor_id: Optional[str]):
        if mentor_id is not None:
            return await self.airtable.update_request(self.record, mentor_id)

    async def update_message(self):
        """
        Builds the slack API call to update the original message
        """
        response = {
            'channel': self['channel']['id'],
            'ts': self['message_ts'],
            'attachments': self['original_message']['attachments']
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
            "actions": [{
                'name': f'{self.record}',
                "text": f"Reset claim",
                "type": "button",
                "style": "danger",
                "value": "reset_claim_mentee",
            }]
        }

    def mentee_unclaimed_attachment(self) -> dict:
        return {
            'text': f"Reset by <@{self.clicker}> at"
            f" <!date^{now()}^ {{date_num}} {{time_secs}}|Failed to parse time>",
            'fallback': '',
            'color': '#3AA3E3',
            'callback_id': 'claim_mentee',
            'attachment_type': 'default',
            'actions': [{
                'name': f'{self.record}',
                'text': 'Claim Mentee',
                'type': 'button',
                'style': 'primary',
                'value': 'mentee_claimed'
            }]
        }
