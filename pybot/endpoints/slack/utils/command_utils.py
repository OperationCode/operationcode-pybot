from slack import methods

from pybot.endpoints.slack.utils.slash_repeat import repeat_items


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


def get_slash_repeat_channels_messages(user_id, channel):
    response_type = {'ephemeral': methods.CHAT_POST_EPHEMERAL,
                     'message': methods.CHAT_POST_MESSAGE}

    url = 'https://github.com/OperationCode/operationcode_docs/blob/master/community/slack_channel_guide.md'
    message = f':exclamation:Channel Guide :exclamation: {url}'
    values_dict = {'type': 'ephemeral',
                'message': {'channel': channel, 'user': user_id, 'text': message}}
    return response_type[values_dict['type']], values_dict['message']
