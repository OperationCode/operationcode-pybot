import logging
import re
from datetime import datetime, timedelta
from random import random, choice
from typing import Dict, List, Pattern, Generator

logger = logging.getLogger(__name__)


class TechTermsGrabber:
    # shared across all instances
    TERM_URL = (
        "https://raw.githubusercontent.com/togakangaroo/tech-terms/master/terms.org"
    )
    LAST_UPDATE = datetime(2012, 1, 1, 1, 1)
    HOURS_BEFORE_REFRESH = 3

    def __init__(self, app):
        self.app = app

    def get_terms(self):
        if (
            datetime.now() - timedelta(hours=self.HOURS_BEFORE_REFRESH)
        ) > self.LAST_UPDATE:
            self.TERMS = self._update_terms()
        return self.TERMS

    async def _update_terms(self) -> Dict[str, list]:
        two_col_org_row: Pattern[str] = self._compile_regex_from_parts()

        content = await self._grab_data_from_github()
        lines: List[str] = content.splitlines()

        return {
            x["term"].lower(): f'{x["term"]} is {x["definition"]}'
            for x in self._filter_matches(lines, two_col_org_row)
        }

    async def _grab_data_from_github(self) -> str:
        async with self.app.http_session.get(self.TERM_URL) as r:
            r.raise_for_status()
            return await r.text(encoding="utf-8")

    def _compile_regex_from_parts(self) -> Pattern[str]:
        n_spaces_pipe_n_spaces = "\\s*\\|\\s*"
        non_greedy_group_of_chars = ".*?"
        regex_string = (
            f"^{n_spaces_pipe_n_spaces}(?P<term>{non_greedy_group_of_chars})"
            f"{n_spaces_pipe_n_spaces}(?P<definition>{non_greedy_group_of_chars}){n_spaces_pipe_n_spaces}$"
        )

        return re.compile(regex_string)

    def _filter_matches(
        self, lines: List[str], two_col_org_row: Pattern[str]
    ) -> Generator[dict, None, None]:
        for line in lines:
            match = two_col_org_row.match(line).groupdict()
            if match.get("term") and match.get("definition"):
                yield match


class TechTerms:
    # shared across all instances
    TERMS = {}
    ADD_GITHUB_CHANCE = 0.25

    def __init__(self, channel: str, user: str, input_text: str, app):

        self.channel_id = channel
        self.user_id = user
        self.input_text = self.remove_tech(input_text)
        self.app = app
        self.response_params = None

    def remove_tech(self, initial_input):
        return initial_input.split("!tech", 1)[1]

    async def grab_values(self) -> dict:
        if not self.input_text:
            return {"message": {"text": self._help_text(), "channel": self.channel_id}}

        else:
            if not self.response_params:
                await self._parse_input()

            if self.input_text:
                return {"message": self._grab_term(term=self.input_text)}

        return {"message": self._grab_term()}

    async def _parse_input(self) -> None:
        grabber = TechTermsGrabber(self.app)
        self.TERMS = await grabber.get_terms()

    def _help_text(self):
        return (
            "Use this to find descriptions of common and useful tech terms. Examples:\n"
            + '"!tech Java" or "!tech prolog"'
            + self._source_text()
        )

    def _source_text(self):
        return (
            "\nTech Terms source: <https://github.com/togakangaroo/tech-terms|github>"
        )

    def _convert_key_to_dict(self, key: str, random_val: bool = False) -> dict:
        return {"term": key, "random": random_val, "definition": f"{self.TERMS[key]}"}

    def _grab_term(self, term=None):
        if term and self.TERMS.get(term.lower().strip()):
            term_key: str = term.lower().strip()
            return self._build_response_text(self._convert_key_to_dict(term_key))

        return self._build_response_text(self._random_term())

    def _build_response_text(self, term: dict) -> dict:
        return {"channel": self.channel_id, "text": self._serialize_term(term)}

    def _random_term(self) -> dict:
        item = choice(list(self.TERMS.keys()))
        return self._convert_key_to_dict(item, random_val=True)

    def _serialize_term(self, term: Dict[str, str]) -> str:
        random_text = "Selected random term:\n"
        addnl = self._source_text() if random() < self.ADD_GITHUB_CHANCE else ""

        return f'{random_text if term["random"] else ""} {term["definition"]}{addnl}'
