import os
from typing import Any
from pyairtable import Table

from modules.utils import table_fields


class BaseAirtableTable(Table):
    def __init__(self, table_name: str):
        super().__init__(
            api_key=os.getenv("AIRTABLE_API_KEY"),
            base_id=os.getenv("AIRTABLE_BASE_ID"),
            table_name=f"{table_name}",
        )

    @property
    def table_fields(self) -> list[str]:
        """Returns snake cased columns (fields in Airtable parlance) on the table

        :return: list of fields
        :rtype: list[str]
        """
        return table_fields(self)

    def update_record(
        self, airtable_id: str, fields_to_update: dict[str, Any]
    ) -> dict[str, Any]:
        return self.update(airtable_id, fields=fields_to_update, typecast=True)

    def create_record(self, record_to_create: dict[str, Any]) -> dict[str, Any]:
        return self.create(fields=record_to_create, typecast=True)
