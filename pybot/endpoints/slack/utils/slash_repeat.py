from typing import Iterable


def default_repeat_message(message_options: Iterable) -> str:
    return ('That is not a valid option valid options are:\n ' +
            ''.join([f'->\t"{key}"\n' for key in message_options]))


def modify_params(modify_options: dict) -> dict:
    message = {
        "channel": modify_options['channel_id'],
        "attachments": [
            {
                "pretext": "Text before block",
                "title": "Text of link",
                "title_link": "https://groove.hq/path/to/ticket/1943",

            }
        ]
    }

    message['attachments'][0]['pretext'] = f'<@{modify_options["slack_id"]}>: {modify_options["pretext"]}'
    message['attachments'][0]['title'] = modify_options['title']
    message['attachments'][0]['title_link'] = modify_options["link"]

    return message


def repeat_items(requested_text: str, slack_id: str, channel_id: str) -> dict:
    messages = {
        '10000': {'link': 'https://xkcd.com/1053/',
                  'title': 'XKCD: lucky',
                  'pretext': 'Looks like you\'re one of the lucky 10,000 today!'},
        'asking': {'link': 'http://sol.gfxile.net/dontask.html',
                   'title': 'Asking Questions',
                   'pretext': 'You can just ask, we\'re all here to help'}
    }

    modify_options = messages.get(requested_text)

    if modify_options:
        modify_options['slack_id'] = slack_id
        modify_options['channel_id'] = channel_id
        return {'type': 'message', 'message': modify_params(modify_options)}
    else:
        return {'type': 'ephemeral',
                'message': {'channel': channel_id, 'user': slack_id, 'text': default_repeat_message(messages.keys())}}
