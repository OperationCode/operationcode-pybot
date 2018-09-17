from slack import methods

from pybot.endpoints.slack.utils.slash_repeat import repeat_items


async def get_slash_here_messages(mod_id, channel, slack, text):
    channel_members_response = await slack.query(methods.CONVERSATIONS_MEMBERS, data={'channel': channel})
    member_list = ' '.join([f'<@{member}>' for member in channel_members_response['members']])
    announcement = f':exclamation:Announcement:exclamation: <@{mod_id}>: {text}'
    return announcement, member_list


async def get_slash_repeat_messages(user_id, channel, slack, text):
    display_name = await slack.query(methods.USERS_INFO, data={'user': user_id})

    response_type = {'ephemeral': methods.CHAT_POST_EPHEMERAL,
                     'message': methods.CHAT_POST_MESSAGE}

    values_dict = repeat_items(text, display_name, channel)
    return response_type[values_dict['type']], values_dict['message']
