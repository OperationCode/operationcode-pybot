from typing import Iterable


def find_resources() -> dict:
    return {'link': 'https://github.com/OperationCode/resources_api/blob/master/db_setup/resources.yml',
            'title': 'A big list of resources',
            'pretext': 'Would you like some resources.yml?'}


def ask() -> dict:
    return {'link': 'http://sol.gfxile.net/dontask.html',
            'title': 'Asking Questions',
            'pretext': 'You can just ask, we\'re all here to help'}


def default_repeat_message(message_options: Iterable) -> str:
    keys = ''.join([f'->\t"{key}"\n' for key in message_options])
    return 'That is not a valid option valid options are:\n ' + keys


def modify_params(modify_options: dict) -> dict:
    message = {
        "attachments": [
            {
                "pretext": "Text before block",
                "title": "Text of link",
                "title_link": "https://groove.hq/path/to/ticket/1943",

            }
        ]
    }

    message['attachments'][0]['pretext'] = f'{modify_options["display_name"]}: {modify_options["pretext"]}'
    message['attachments'][0]['title'] = modify_options['title']
    message['attachments'][0]['title_link'] = modify_options["link"]

    return message


def repeat_items(requested_text: str, display_name: str, channel_id: str) -> dict:
    messages = {
        '10000': {'link': 'https://xkcd.com/1053/',
                  'title': 'XKCD: lucky',
                  'pretext': 'Looks like you\'re one of the lucky 10,000 today!'},
        'ask': ask(),
        'asking': ask(),
        'ldap': {'link': 'http://large-type.com/#yes',
                 'title': 'Is someone complaining about LDAP?',
                 'pretext': 'What\'s that I hear about LDAP?'},
        # TODO: make this into a url call.
        'resources': find_resources(),
        'resource': find_resources(),
    }

    modify_options = messages.get(requested_text.lower())

    if modify_options:
        modify_options['display_name'] = display_name
        return {'type': 'message', 'message': modify_params(modify_options)}
    else:
        return {'type': 'emphemeral',
                'message': {'channel': channel_id, 'text': default_repeat_message(messages.keys())}}


if __name__ == '__main__':
    import json

    print(json.dumps(repeat_items('reSourCe', '123safs', 'mike')))
