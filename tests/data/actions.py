import json
from enum import Enum

claim_event = {
    'type': 'interactive_message',
    'user': {'id': 'U123'},
    'actions': [{'name': 'rec123', 'value': 'mentee_claimed'}],
    'original_message': {
        'text': 'some text',
        'attachments': [
            {
                'text': 'some text', 'actions': [{'name': 'rec123', 'value': 'mentee_unclaimed'}],
            }
        ],
    }, 'channel': {'id': 'abc'},
    'message_ts': '123123.123',
    'callback_id': 'claim_mentee',
    "token": "supersecuretoken",
    "team_id": "T000AAA0A",
    "api_app_id": "A0AAAAAAA",
    "authed_teams": ["T000AAA0A"],
    "event_id": "AAAAAAA",
    "event_time": 123456789,
}

unclaim_event = {
    'type': 'interactive_message',
    'user': {'id': 'U123'},
    'actions': [{'name': 'rec123', 'value': 'mentee_unclaimed'}],
    'original_message': {
        'text': 'some text',
        'attachments': [
            {
                'text': 'some text', 'actions': [{'name': 'rec123', 'value': 'mentee_unclaimed'}],
            }
        ],
    },
    'channel': {'id': 'abc'},
    'message_ts': '123123.123',
    'callback_id': 'claim_mentee',
    "token": "supersecuretoken",
    "team_id": "T000AAA0A",
    "api_app_id": "A0AAAAAAA",
    "authed_teams": ["T000AAA0A"],
    "event_id": "AAAAAAA",
    "event_time": 123456789,
}

raw_claim_event = {"payload": json.dumps(claim_event)}
raw_unclaim_event = {"payload": json.dumps(unclaim_event)}


class Action(Enum):
    claim_mentee = raw_claim_event
    unclaim_mentee = raw_unclaim_event
