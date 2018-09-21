import logging
import re
from datetime import datetime, timedelta
from random import random
from typing import Dict, List, Pattern, Generator

logger = logging.getLogger(__name__)


class TechTermsGrabber:
    # shared across all instances
    TERM_URL = 'https://raw.githubusercontent.com/togakangaroo/tech-terms/master/terms.org'
    LAST_UPDATE = datetime(2012, 1, 1, 1, 1)
    HOURS_BEFORE_REFRESH = 3

    def __init__(self, app):
        self.app = app

    def get_terms(self):
        if (datetime.now() - timedelta(hours=self.HOURS_BEFORE_REFRESH)) > self.LAST_UPDATE:
            self.TERMS = self._update_terms()
        return self.TERMS

    async def _update_terms(self) -> Dict[str, list]:
        two_col_org_row: Pattern[str] = self._compile_regex_from_parts()

        content = await self._grab_data_from_github()

        lines: List[str] = content.splitlines()

        return {x['term']: x['definition'] for x in self._filter_matches(lines, two_col_org_row)}

    async def _grab_data_from_github(self) -> str:
        async with self.app.http_session.get(self.TERM_URL) as r:
            r.raise_for_status()
            data = await r.json()
            return data.decode('utf-8')

    def _compile_regex_from_parts(self) -> Pattern[str]:
        n_spaces_pipe_n_spaces = '\\s*\\|\\s*'
        non_greedy_group_of_chars = '.*?'
        regex_string = f'^{n_spaces_pipe_n_spaces}(?P<term>{non_greedy_group_of_chars})' \
                       f'{n_spaces_pipe_n_spaces}(?P<definition>{non_greedy_group_of_chars}){n_spaces_pipe_n_spaces}$'

        return re.compile(regex_string)

    def _filter_matches(self, lines: List[str], two_col_org_row: Pattern[str]) -> Generator[dict, None, None]:
        for line in lines:
            match = two_col_org_row.match(line).groupdict()
            if match.get('term') and match.get('definition'):
                yield match


class TechTerms:
    # shared across all instances
    TERMS = {}

    def __init__(self, channel: str, user: str, input_text: str, user_name: str, app):

        self.channel_id = channel
        self.user_id = user
        self.input_text = input_text
        self.user_name = user_name
        self.app = app

        self.response_params = self._parse_input()

    def grab_values(self) -> dict:
        if not self.input_text:
            return {'type': 'epehmeral', 'message': self._grab_term(), }

        else:

            split_items: List[str] = self.input_text.split()
            if split_items[0] == 'loud':
                return {'type': 'loud', 'message': self._grab_term(split_items)}

        return {'type': 'epehmeral', 'message': self._grab_term(), }

    async def _parse_input(self) -> None:
        self.TERMS = await TechTermsGrabber(self.app).get_terms()

    def _convert_key_to_dict(self, key: str) -> dict:
        return {'term': key, 'definition': self.TERMS[key]}

    def _grab_term(self, term=None):
        if isinstance(term, list) and len(term) > 1 and self.TERMS.get(term[1]):
            term_key: str = self.TERMS.get(term[1])
            return self._build_response_text(self._convert_key_to_dict(term_key))

        return self._build_response_text(self._random_term())

    def _build_response_text(self, term: dict) -> dict:
        return {'user': self.user_id, 'channel': self.channel_id,
                'text': f'{term["term"]} is {term["definition"]}'}

    def _random_term(self) -> dict:
        choice = random.choice(self.TERMS.keys())
        return self._convert_key_to_dict(choice)

    def _serialize_term(self, term: Dict[str, str]) -> str:
        return f'{term["term"]} is {term["definition"]}'
