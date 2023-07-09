import logging  # noqa: D100
from typing import Any

from pydantic import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.daily_programmer_models import DailyProgrammerInfo
from modules.utils import snake_case

logger = logging.getLogger(__name__)


class DailyProgrammerTable(BaseAirtableTable):  # noqa: D101
    def __init__(self):  # noqa: ANN101, ANN204, D107
        super().__init__("Daily Programmer")

    @staticmethod
    def parse_daily_programmer_row(row: dict[str, Any]) -> DailyProgrammerInfo:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return DailyProgrammerInfo(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    def retrieve_valid_daily_programmer_row_by_slug(  # noqa: D102
        self,  # noqa: ANN101
        slug: str,
    ) -> DailyProgrammerInfo:
        return self.parse_daily_programmer_row(
            self.first(
                formula=f"{{Slug}} = '{slug}'",
                view="Valid",
            ),
        )

    def retrieve_valid_daily_programmer_by_view(  # noqa: D102
        self,  # noqa: ANN101
        view_name: str,
    ) -> dict[str, DailyProgrammerInfo]:
        logger.info("STAGE: Retrieving daily programmer rows by view")
        logger.debug(f"With view_name: {view_name}")  # noqa: G004
        messages = {}
        for row in self.all(view=view_name):
            parsed_row = self.parse_daily_programmer_row(row)
            messages[parsed_row.slug] = parsed_row
        return messages
