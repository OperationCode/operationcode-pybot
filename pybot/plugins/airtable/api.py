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
        auth_header = {"Authorization": f"Bearer {self.api_key}"}

        async with self.session.get(url, headers=auth_header, **kwargs) as r:
            return await r.json()

    async def patch(self, url, **kwargs):
        auth_header = {"authorization": f"Bearer {self.api_key}"}
        async with self.session.patch(url, headers=auth_header, **kwargs) as r:
            r.raise_for_status()
            return await r.json()

    async def post(self, url, **kwargs):
        auth_header = {"authorization": f"Bearer {self.api_key}"}
        async with self.session.post(url, headers=auth_header, **kwargs) as r:
            return await r.json()

    async def _depaginate_records(self, url, params, offset):
        records = []
        while offset:
            params["offset"] = offset
            response = await self.get(url, params=params)
            # Check for error response during pagination
            if "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                logger.error(f"Airtable API error during pagination: {error_msg}")
                break
            records.extend(response.get("records", []))
            offset = response.get("offset")

        return records

    def table_url(self, table_name, record_id=None):
        url = f"{self.API_ROOT}{self.base_key}/{table_name}"
        if record_id:
            url += f"/{record_id}"
        return url

    async def get_name_from_record_id(self, table_name: str, record_id):
        if self.record_id_to_name[table_name]:
            return self.record_id_to_name[table_name].get(record_id)

        url = self.table_url("Services")
        params = {"fields[]": "Name"}
        res_json = await self.get(url, params=params)

        # Check for Airtable API error response
        if "error" in res_json:
            error_msg = res_json["error"].get("message", "Unknown error")
            logger.error(f"Airtable API error for Services table: {error_msg}")
            return None

        records = res_json["records"]
        # Skip records that don't have a Name field (Airtable omits empty fields)
        self.record_id_to_name[table_name] = {
            record["id"]: record["fields"]["Name"]
            for record in records
            if "Name" in record.get("fields", {})
        }
        return self.record_id_to_name[table_name].get(record_id)

    async def get_row_from_record_id(self, table_name: str, record_id: str) -> dict:
        url = self.table_url(table_name, record_id)
        try:
            res_json = await self.get(url)

            # Check for Airtable API error response
            if "error" in res_json:
                error_msg = res_json["error"].get("message", "Unknown error")
                logger.error(
                    f"Airtable API error for record {record_id} in {table_name}: {error_msg}"
                )
                return {}

            return res_json["fields"]
        except Exception:
            logger.exception(f"Couldn't get row from record id {record_id} in {table_name}")
            return {}

    async def get_all_records(self, table_name, field=None):
        url = self.table_url(table_name)
        if field:
            params = {"fields[]": field}
            res_json = await self.get(url, params=params)
        else:
            res_json = await self.get(url)

        # Check for Airtable API error response
        if "error" in res_json:
            error_msg = res_json["error"].get("message", "Unknown error")
            error_type = res_json["error"].get("type", "Unknown type")
            logger.error(f"Airtable API error for table '{table_name}': {error_type} - {error_msg}")
            raise ValueError(
                f"Airtable API error: {error_type} - {error_msg}. "
                f"Check AIRTABLE_API_KEY (must be a Personal Access Token starting with 'pat...') "
                f"and ensure it has access to base {self.base_key}"
            )

        if field:
            # Skip records that don't have the field (Airtable omits empty fields)
            return [
                record["fields"][field]
                for record in res_json["records"]
                if field in record.get("fields", {})
            ]
        else:
            return res_json["records"]

    async def find_mentors_with_matching_skillsets(self, skillsets):
        url = self.table_url("Mentors")
        params = MultiDict([("fields", "Email"), ("fields", "Skillsets"), ("fields", "Slack Name")])
        skillsets = skillsets.split(",")
        response = await self.get(url, params=params)

        # Check for Airtable API error response
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Airtable API error for Mentors table: {error_msg}")
            return []

        offset = response.get("offset")
        mentors = response["records"]

        if offset:
            additional_mentors = await self._depaginate_records(url, params, offset)
            mentors.extend(additional_mentors)

        partial_match = []
        complete_match = []
        try:
            for mentor in mentors:
                if all(skillset in mentor["fields"].get("Skillsets", []) for skillset in skillsets):
                    complete_match.append(mentor["fields"])
                if any(
                    mentor["fields"] not in complete_match
                    and skillset in mentor["fields"].get("Skillsets", [])
                    for skillset in skillsets
                ):
                    partial_match.append(mentor["fields"])
        except Exception:
            logger.exception("Exception while trying to filter mentors by skillset")
            return []

        if len(complete_match) < 5:
            complete_match += partial_match

        return complete_match or partial_match

    async def find_records(self, table_name: str, field: str, value: str) -> list:
        url = self.table_url(table_name)

        params = {"filterByFormula": f"FIND(LOWER('{value}'), LOWER({{{field}}}))"}

        try:
            response = await self.get(url, params=params)

            # Check for Airtable API error response
            if "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                logger.error(f"Airtable API error for table '{table_name}': {error_msg}")
                return []

            return response["records"]
        except Exception:
            logger.exception(f"Exception when attempting to get {field} from {table_name}")
            return []

    async def update_request(self, request_record, mentor_id):
        url = self.table_url("Mentor Request", request_record)
        data = {"fields": {"Mentor Assigned": [mentor_id] if mentor_id else None}}
        return await self.patch(url, json=data)

    async def add_record(self, table, json):
        url = self.table_url(table)
        return await self.post(url, json=json)
