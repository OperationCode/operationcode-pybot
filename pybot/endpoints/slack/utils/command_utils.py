from slack import methods


async def get_slash_here_messages(mod_id, channel, slack, text):
    channel_members_response = await slack.query(methods.CONVERSATIONS_MEMBERS, data={'channel': channel})
    member_list = ' '.join([f'<@{member}>' for member in channel_members_response['members']])
    announcement = f':exclamation:Announcement:exclamation: <@{mod_id}>: {text}'
    return announcement, member_list
