from slack import methods
from slack.actions import Action
from slack.io.abc import SlackAPI

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

    @classmethod
    def selected_option(cls, attachment):
        action = attachment['actions'][0]
        if 'selected_options' in action:
            return action['selected_options'][0]['value']
        return ''

    @property
    def attachments(self):
        return self.action['attachments']

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
            'ts': self.action['ts'],
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
            'Email': email
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

        self.action['attachments'] = [done_attachment]
        return self.update(slack)

    def clear_skillsets(self):
        self.attachments[SKILLSET_INDEX]['text'] = ''

    def update(self, slack: SlackAPI):
        return slack.query(methods.CHAT_UPDATE, self.update_params)
