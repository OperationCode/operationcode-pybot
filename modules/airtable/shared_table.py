import os  # noqa: D100
from typing import Any

from pyairtable import Table

from modules.utils import table_fields


class BaseAirtableTable(Table):  # noqa: D101
    def __init__(self, table_name: str):  # noqa: ANN101, ANN204, D107
        super().__init__(
            api_key=os.getenv("AIRTABLE_API_KEY"),
            base_id=os.getenv("AIRTABLE_BASE_ID"),
            table_name=f"{table_name}",
        )

    @property
    def table_fields(self) -> list[str]:  # noqa: ANN101
        """Returns snake cased columns (fields in Airtable parlance) on the table.

        :return: list of fields
        :rtype: list[str]
        """
        return table_fields(self)

    def update_record(  # noqa: D102
        self,  # noqa: ANN101
        airtable_id: str,
        fields_to_update: dict[str, Any],
    ) -> dict[str, Any]:
        return self.update(airtable_id, fields=fields_to_update, typecast=True)

    def create_record(self, record_to_create: dict[str, Any]) -> dict[str, Any]:  # noqa: ANN101, D102
        return self.create(fields=record_to_create, typecast=True)
