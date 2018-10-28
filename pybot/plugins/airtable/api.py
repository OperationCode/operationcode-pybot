import logging
from functools import lru_cache

from multidict import MultiDict

logger = logging.getLogger(__name__)


class AirtableAPI:
    API_ROOT = 'https://api.airtable.com/v0/'
    services_id_to_service = None

    def __init__(self, session, api_key, base_key):
        self.session = session
        self.api_key = api_key
        self.base_key = base_key

    async def get(self, url, **kwargs):
        auth_header = {f'Authorization': f"Bearer {self.api_key}"}

        async with self.session.get(url, headers=auth_header, **kwargs) as r:
            r.raise_for_status()
            return await r.json()

    async def patch(self, url, **kwargs):
        auth_header = {f'authorization': f"Bearer {self.api_key}"}
        async with self.session.patch(url, headers=auth_header, **kwargs) as r:
            r.raise_for_status()
            return await r.json()

    def table_url(self, table_name, record_id=None):
        url = f'{self.API_ROOT}{self.base_key}/{table_name}'
        if record_id:
            url += f'/{record_id}'
        return url

    async def translate_service_id(self, service_id):
        if self.services_id_to_service:
            return self.services_id_to_service[service_id]

        url = self.table_url("Services")
        params = {'fields[]': 'Name'}
        res_json = await self.get(url, params=params)
        records = res_json['records']
        self.services_id_to_service = {record['id']: record['fields']['Name'] for record in records}
        return self.services_id_to_service[service_id]

    async def get_mentor_from_record_id(self, record_id: str) -> dict:
        url = self.table_url("Mentors", record_id)
        try:
            res_json = await self.get(url)
            return res_json['fields']
        except Exception as ex:
            return {}

    async def find_mentors_with_matching_skillsets(self, skillsets):
        url = self.table_url("Mentors")
        params = MultiDict([('fields', 'Email'), ('fields', 'Skillsets'), ('fields', 'Slack Name')])
        skillsets = skillsets.split(',')
        response = await self.get(url, params=params)
        mentors = response['records']
        partial_match = []
        complete_match = []
        try:
            for mentor in mentors:
                if all(skillset in mentor['fields']['Skillsets'] for skillset in skillsets):
                    complete_match.append(mentor['fields'])
                if any(mentor['fields'] not in complete_match and
                       skillset in mentor['fields']['Skillsets'] for skillset in skillsets):
                    partial_match.append(mentor['fields'])
        except Exception as e:
            return []

        if len(complete_match) < 3:
            complete_match += partial_match

        return complete_match or partial_match

    async def mentor_id_from_slack_email(self, email):
        url = self.table_url("Mentors")
        params = {"filterByFormula": f"FIND(LOWER('{email}'), LOWER({{Email}}))"}

        try:
            response = await self.get(url, params=params)
            records = response['records']
            if records:
                return records[0]['id']
            else:
                return ''
        except Exception as ex:
            logger.exception('Exception when attempting to get mentor id from slack email.', ex)
            return ''

    async def update_request(self, request_record, mentor_id):
        url = self.table_url("Mentor Request", request_record)
        data = {
            "fields": {
                "Mentor Assigned": [mentor_id] if mentor_id else None
            }}
        return await self.patch(url, json=data)
