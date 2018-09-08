from slack import methods


async def get_slash_here_message(channel, slack, text):
    channel_members_response = await slack.query(methods.CONVERSATIONS_MEMBERS, data={'channel': channel})
    member_list = [f'<@{member}>' for member in channel_members_response['members']]
    message = f"{' '.join(member_list)}  {text}"
    return message