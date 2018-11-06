TEAM_JOIN = {
        "token": "supersecuretoken",
        "team_id": "T000AAA0A",
        "api_app_id": "A0AAAAAAA",
        "event": {
            "type": "team_join",
            "channel": "C00000A00",
            "user": {"id": "U0AAAA",
                     "team_id": "T000AAA0A",
                     "name": "test",
                     "real_name": "test testerson",
                     },
            "event_ts": "123456789.000001",
        },
        "type": "event_callback",
        "authed_teams": ["T000AAA0A"],
        "event_id": "AAAAAAA",
        "event_time": 123456789,
    }

new_message = {'type': 'message', 'user': 'U8FDR1603', 'text': 'test3',
               'client_msg_id': '025cc728-fcb5-4dd7-8920-619a605bb631', 'ts': '1540497949.000100',
               'channel': 'GDNHHNCTV', 'event_ts': '1540497949.000100', 'channel_type': 'mpim'}
edit_message = {
    "token": "supersecuretoken",
    "team_id": "T000AAA0A",
    "api_app_id": "A0AAAAAAA",
    "type": "event_callback",
    "authed_teams": ["T000AAA0A"],
    "event_id": "AAAAAAA",
    "event_time": 123456789,
    'event': {'type': 'message',
              'message': {'type': 'message',
                          'user': 'U8FDR1603',
                          'text': 'nevermind',
                          'client_msg_id': '9aff714d-8674-42fc-986c-0c1c06cca3fc',
                          'edited': {'user': 'U8FDR1603', 'ts': '1540497210.000000'},
                          'ts': '1540497204.000100'
                          },
              'subtype': 'message_changed',
              'hidden': True,
              'channel': 'C8DA69KM4',
              'previous_message': {'type': 'message', 'user': 'U8FDR1603', 'text': 'two',
                                   'client_msg_id': '9aff714d-8674-42fc-986c-0c1c06cca3fc',
                                   'ts': '1540497204.000100'},
              'event_ts': '1540497210.000100', 'ts': '1540497210.000100', 'channel_type': 'channel'}
}
delete_message = {'type': 'message', 'deleted_ts': '1540497676.000100', 'subtype': 'message_deleted', 'hidden': True,
                  'channel': 'GDNHHNCTV',
                  'previous_message': {'type': 'message', 'user': 'U8FDR1603', 'text': 'testing3',
                                       'client_msg_id': 'b5694bd6-6ed0-4ddd-bf84-3e2c8165c624',
                                       'ts': '1540497676.000100'}, 'event_ts': '1540497684.000100',
                  'ts': '1540497684.000100', 'channel_type': 'mpim'}

MESSAGE_EDIT = {
    "token": "supersecuretoken",
    "team_id": "T000AAA0A",
    "api_app_id": "A0AAAAAAA",
    "event": {
        "type": "message",
        "message": {
            "type": "message",
            "user": "U000AA000",
            "text": "hello world",
            "edited": {"user": "U000AA000", "ts": "1513882449.000000"},
            "ts": "123456789.000001",
        },
        "subtype": "message_changed",
        "hidden": True,
        "channel": "C00000A00",
        "previous_message": {
            "type": "message",
            "user": "U000AA000",
            "text": "foo bar",
            "ts": "123456789.000001",
        },
        "event_ts": "123456789.000002",
        "ts": "123456789.000002",
    },
    "type": "event_callback",
    "authed_teams": ["T000AAA0A"],
    "event_id": "AAAAAAA",
    "event_time": 123456789,
}

MESSAGE_DELETE = {
    "token": "supersecuretoken",
    "team_id": "T000AAA0A",
    "api_app_id": "A0AAAAAAA",
    "event": {
        "type": "message",
        "message": {
            "type": "message",
            "user": "U000AA000",
            "text": "hello world",
            "edited": {"user": "U000AA000", "ts": "1513882449.000000"},
            "ts": "123456789.000001",
        },
        "subtype": "message_deleted",
        "hidden": True,
        "channel": "C00000A00",
        "previous_message": {
            "type": "message",
            "user": "U000AA000",
            "text": "foo bar",
            "ts": "123456789.000001",
        },
        "event_ts": "123456789.000002",
        "ts": "123456789.000002",
    },
    "type": "event_callback",
    "authed_teams": ["T000AAA0A"],
    "event_id": "AAAAAAA",
    "event_time": 123456789,
}

PLAIN_MESSAGE = {
    "token": "supersecuretoken",
    "team_id": "T000AAA0A",
    "api_app_id": "A0AAAAAAA",
    "event": {
        "type": "message",
        "message": {
            "type": "message",
            "user": "U000AA000",
            "text": "hello world",
            "edited": {"user": "U000AA000", "ts": "1513882449.000000"},
            "ts": "123456789.000001",
        },
        "channel": "C00000A00",
        "event_ts": "123456789.000002",
        "ts": "123456789.000002",
    },
    "type": "event_callback",
    "authed_teams": ["T000AAA0A"],
    "event_id": "AAAAAAA",
    "event_time": 123456789,
}
