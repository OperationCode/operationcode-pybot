from typing import Iterable


# TODO: use the github api to find the file even if location changes
def find_resources() -> dict:
    return {'link': 'https://github.com/OperationCode/resources_api/blob/master/resources.yml',
            'title': 'A big list of resources',
            'pretext': 'Would you like some resources.yml?'}


def ask() -> dict:
    return {'link': 'http://sol.gfxile.net/dontask.html',
            'title': 'Asking Questions',
            'pretext': 'You can just ask, we\'re all here to help'}


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
    # TODO: get better way of only showing unique values
    # for keys instead of my wonky way of adding more options
    messages = {
        '10000': {'link': 'https://xkcd.com/1053/',
                  'title': 'XKCD: lucky',
                  'pretext': 'Looks like you\'re one of the lucky 10,000 today!'},
        'ask': ask(),
        'asking': ask(),
        'ldap': {'link': 'http://large-type.com/#yes',
                 'title': 'Is someone complaining about LDAP?',
                 'pretext': 'What\'s that I hear about LDAP?'},
        'merge': {'link': 'http://large-type.com/#WILL',
                 'title': 'Who is that force merging to master?',
                 'pretext': 'git push -f origin master'},
        'firstpr': {'link': 'https://goo.gl/forms/r02wt0pBNhkxYciI3',
                    'title': 'Get your sticker here!',
                    'pretext': ':firstpr:' },
        'channels': {'link': 'https://github.com/OperationCode/operationcode_docs/blob/master/community/slack_channel_guide.md',
                     'title': 'Channel Guide!',
                     'pretext': 'Check out the Channel Guide!' },
        # TODO: make this into a url call.
        'resources': find_resources(),
        'resource': find_resources(),
    }

    modify_options = messages.get(requested_text.lower())

    if modify_options:
        modify_options['slack_id'] = slack_id
        modify_options['channel_id'] = channel_id
        return {'type': 'message', 'message': modify_params(modify_options)}
    else:
        return {'type': 'ephemeral',
                'message': {'channel': channel_id, 'user': slack_id, 'text': default_repeat_message(messages.keys())}}
