from typing import MutableMapping, Optional

from slack import methods
from slack.actions import Action
from slack.io.abc import SlackAPI

from pybot.endpoints.slack.utils.action_messages import now
from pybot.plugins.airtable.api import AirtableAPI

SERVICE_INDEX = 0
SKILLSET_INDEX = 1
MENTOR_INDEX = 2
DETAILS_INDEX = 3
GROUP_INDEX = 4
SUBMIT_INDEX = 5


class MentorRequest:

    def __init__(self, action: Action, channel=None):
        self.action = action
        self.channel = channel

    def __getitem__(self, item):
        return self.action[item]

    def __setitem__(self, key, value):
        self.action[key] = value

    @classmethod
    def selected_option(cls, attachment):
        action = attachment['actions'][0]
        if 'selected_options' in action:
            return action['selected_options'][0]['value']
        return ''

    @property
    def attachments(self):
        return self['attachments']

    @property
    def service(self):
        attachment = self.attachments[SERVICE_INDEX]
        return self.selected_option(attachment)

    @service.setter
    def service(self, new_service):
        action = self.attachments[SERVICE_INDEX]['actions'][0]
        action['selected_options'] = [{'value': new_service, 'text': new_service}]
        self.attachments[SERVICE_INDEX]['color'] = ''

    @property
    def skillsets(self):
        if 'text' in self.attachments[SKILLSET_INDEX]:
            return self.attachments[SKILLSET_INDEX]['text'].split('\n')
        return []

    def add_skillset(self, skillset):
        if skillset not in self.skillsets:
            skills = self.skillsets
            skills.append(skillset)
        else:
            skills = self.skillsets
        self.attachments[SKILLSET_INDEX]['text'] = '\n'.join(skills)

    @property
    def mentor(self):
        attachment = self.attachments[MENTOR_INDEX]
        return self.selected_option(attachment)

    @mentor.setter
    def mentor(self, new_mentor):
        action = self.attachments[MENTOR_INDEX]['actions'][0]
        action['selected_options'] = [{'value': new_mentor, 'text': new_mentor}]
        action['color'] = ''

    @property
    def certify_group(self):
        attachment = self.attachments[GROUP_INDEX]
        return self.selected_option(attachment)

    @certify_group.setter
    def certify_group(self, group):
        action = self.attachments[GROUP_INDEX]['actions'][0]
        action['selected_options'] = [{'value': group, 'text': group}]
        self.attachments[GROUP_INDEX]['color'] = ''

    @property
    def details(self):
        attachment = self.attachments[DETAILS_INDEX]
        if 'text' in attachment:
            return attachment['text']
        return ''

    @details.setter
    def details(self, new_details):
        self.attachments[DETAILS_INDEX]['text'] = new_details

    @property
    def update_params(self):
        return {
            'channel': self.channel,
            'ts': self['ts'],
            'attachments': self.attachments
        }

    def validate_self(self):
        if not self.service or not self.certify_group:
            submit_attachment = self.attachments[SUBMIT_INDEX]
            submit_attachment['text'] = ':warning: Service and group certification are required. :warning:'
            submit_attachment['color'] = 'danger'
            if not self.service:
                self.attachments[SERVICE_INDEX]['color'] = 'danger'
            if not self.certify_group:
                self.attachments[GROUP_INDEX]['color'] = 'danger'
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
        self.attachments[SUBMIT_INDEX]['text'] = (
            f'Something went wrong.\n'
            f'Error Type:{airtable_response["error"]["type"]}\n'
            f'Error Message: {airtable_response["error"]["message"]}'
        )
        self.attachments[SUBMIT_INDEX]['color'] = 'danger'
        return self.update(slack)

    def submission_complete(self, slack: SlackAPI):
        done_attachment = self.attachments[SUBMIT_INDEX]
        done_attachment['text'] = 'Request submitted successfully!'
        done_attachment['actions'] = [{'type': 'button', 'text': 'Dismiss', 'name': 'cancel', 'value': 'cancel'}]

        self['attachments'] = [done_attachment]
        return self.update(slack)

    def clear_skillsets(self):
        self.attachments[SKILLSET_INDEX]['text'] = ''

    def update(self, slack: SlackAPI):
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
        return self.trigger['value']

    def is_claim(self):
        return self.click_type == 'mentee_claimed'

    @property
    def record(self) -> str:
        """ Airtable record ID for the mentor request """
        return self.trigger['name']

    @property
    def clicker(self):
        return self['user']['id']

    @property
    def attachment(self):
        return self['original_message']['attachments'][0]

    @attachment.setter
    def attachment(self, value):
        self['original_message']['attachments'][0] = value

    def claim_request(self, mentor_record):
        if mentor_record:
            self.attachment = self.mentee_claimed_attachment()
        else:
            self.attachment['text'] = f":warning: <@{self.clicker}>'s slack Email not found in Mentor table. :warning:"
            self.should_update = False

        return self.update_airtable(mentor_record)

    def unclaim_request(self):
        self.attachment = self.mentee_unclaimed_attachment()
        return self.update_airtable('')

    async def update_airtable(self, mentor_id: Optional[str]):
        if mentor_id:
            return self.airtable.update_request(self.record, mentor_id)

    async def update_message(self):
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
