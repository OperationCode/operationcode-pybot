import logging
from collections import defaultdict

from multidict import MultiDict

logger = logging.getLogger(__name__)


class AirtableAPI:
    API_ROOT = "https://api.airtable.com/v0/"
    record_id_to_name = defaultdict(dict)

    def __init__(self, session, api_key, base_key):
        self.session = session
        self.api_key = api_key
        self.base_key = base_key

    async def get(self, url, **kwargs):
        auth_header = {f"Authorization": f"Bearer {self.api_key}"}

        async with self.session.get(url, headers=auth_header, **kwargs) as r:
            return await r.json()

    async def patch(self, url, **kwargs):
        auth_header = {f"authorization": f"Bearer {self.api_key}"}
        async with self.session.patch(url, headers=auth_header, **kwargs) as r:
            r.raise_for_status()
            return await r.json()

    async def post(self, url, **kwargs):
        auth_header = {f"authorization": f"Bearer {self.api_key}"}
        async with self.session.post(url, headers=auth_header, **kwargs) as r:
            return await r.json()

    async def _depaginate_records(self, url, params, offset):
        records = []
        while offset:
            params["offset"] = offset
            response = await self.get(url, params=params)
            records.extend(response["records"])
            offset = response.get("offset")

        return records

    def table_url(self, table_name, record_id=None):
        url = f"{self.API_ROOT}{self.base_key}/{table_name}"
        if record_id:
            url += f"/{record_id}"
        return url

    async def get_name_from_record_id(self, table_name: str, record_id):
        if self.record_id_to_name[table_name]:
            return self.record_id_to_name[table_name][record_id]

        url = self.table_url("Services")
        params = {"fields[]": "Name"}
        res_json = await self.get(url, params=params)
        records = res_json["records"]
        self.record_id_to_name[table_name] = {
            record["id"]: record["fields"]["Name"] for record in records
        }
        return self.record_id_to_name[table_name][record_id]

    async def get_row_from_record_id(self, table_name: str, record_id: str) -> dict:
        url = self.table_url(table_name, record_id)
        try:
            res_json = await self.get(url)
            return res_json["fields"]
        except Exception as ex:
            logger.exception(
                f"Couldn't get row from record id {record_id} in {table_name}", ex
            )
            return {}

    async def get_all_records(self, table_name, field=None):
        url = self.table_url(table_name)
        if field:
            params = {"fields[]": field}
            res_json = await self.get(url, params=params)
            return [record["fields"][field] for record in res_json["records"]]
        else:
            res_json = await self.get(url)
            return res_json["records"]

    async def find_mentors_with_matching_skillsets(self, skillsets):
        url = self.table_url("Mentors")
        params = MultiDict(
            [("fields", "Email"), ("fields", "Skillsets"), ("fields", "Slack Name")]
        )
        skillsets = skillsets.split(",")
        response = await self.get(url, params=params)
        offset = response.get("offset")
        mentors = response["records"]

        if offset:
            additional_mentors = await self._depaginate_records(url, params, offset)
            mentors.extend(additional_mentors)

        partial_match = []
        complete_match = []
        try:
            for mentor in mentors:
                if all(
                    skillset in mentor["fields"].get("Skillsets", [])
                    for skillset in skillsets
                ):
                    complete_match.append(mentor["fields"])
                if any(
                    mentor["fields"] not in complete_match
                    and skillset in mentor["fields"].get("Skillsets", [])
                    for skillset in skillsets
                ):
                    partial_match.append(mentor["fields"])
        except Exception as e:
            logger.exception(
                "Exception while trying to find filter mentors by skillset", e
            )
            return []

        if len(complete_match) < 5:
            complete_match += partial_match

        return complete_match or partial_match

    async def find_records(self, table_name: str, field: str, value: str) -> list:
        url = self.table_url(table_name)

        params = {"filterByFormula": f"FIND(LOWER('{value}'), LOWER({{{field}}}))"}

        try:
            response = await self.get(url, params=params)
            return response["records"]
        except Exception as ex:
            logger.exception(
                f"Exception when attempting to get {field} from {table_name}.", ex
            )
            return []

    async def update_request(self, request_record, mentor_id):
        url = self.table_url("Mentor Request", request_record)
        data = {"fields": {"Mentor Assigned": [mentor_id] if mentor_id else None}}
        return await self.patch(url, json=data)

    async def add_record(self, table, json):
        url = self.table_url(table)
        return await self.post(url, json=json)
