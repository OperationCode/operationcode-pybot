from slack import methods

from pybot.endpoints.slack.utils.slash_repeat import repeat_items


def response_type(selected_type: str) -> methods:
    response_type = {'ephemeral': methods.CHAT_POST_EPHEMERAL,
                     'message': methods.CHAT_POST_MESSAGE}

    return response_type[selected_type]


async def get_slash_here_messages(mod_id, channel, slack, text):
    channel_members_response = await slack.query(methods.CONVERSATIONS_MEMBERS, data={'channel': channel})
    member_list = ' '.join([f'<@{member}>' for member in channel_members_response['members']])
    announcement = f':exclamation:Announcement:exclamation: <@{mod_id}>: {text}'
    return announcement, member_list


def get_slash_repeat_messages(user_id, channel, text):
    response_type = {'ephemeral': methods.CHAT_POST_EPHEMERAL,
                     'message': methods.CHAT_POST_MESSAGE}

    values_dict = repeat_items(text, user_id, channel)
    return response_type[values_dict['type']], values_dict['message']


def action_value(attachment):
    action = attachment['actions'][0]
    if 'selected_options' in action:
        return action['selected_options'][0]['value']
    return ''
