from slack import methods


async def get_slash_here_message(channel, slack, text):
    channel_members_response = await slack.query(methods.CONVERSATIONS_MEMBERS, data={'channel': channel})
    member_list = [f'<@{member}>' for member in channel_members_response['members']]
    message = f"{' '.join(member_list)}  {text}"
    return message


async def can_here(channel, user_id, pg):
    async with pg.connection() as pg_con:
        channel_id = await pg_con.fetchval("""
        SELECT channel.id
        from channel where channel.channel_id = $1
        """, channel)

        users = await pg_con.fetch(
            """
        SELECT "user".slack_id
        FROM "user", channels_mods
        WHERE $1 = channels_mods.channel_id
          AND "user".id = channels_mods.user_id
            """, channel_id
        )

        return any(user_id == user['slack_id'] for user in users)
