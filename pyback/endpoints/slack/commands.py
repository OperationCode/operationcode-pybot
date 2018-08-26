import logging

from aiohttp.web_response import Response
from slack import methods

from pyback.endpoints.slack.utils.slash_lunch import split_params, get_random_lunch, build_response_text

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_command('/here', slash_here)
    plugin.on_command('/lunch', slash_lunch)


async def slash_here(command, app):
    channel = command['channel_id']
    slack = app["plugins"]["slack"].api

    authorized = await _can_here(channel, command['user_id'], app["plugins"]["pg"])
    if not authorized:
        return Response(text="You are not authorized to use that command in this channel")

    message = await _get_slash_here_message(channel, slack, command['text'])
    await slack.query(methods.CHAT_POST_MESSAGE, {'channel': channel, 'text': message})


async def slash_lunch(command, app):
    param_dict = split_params(command.get('text'))
    params = (
        ('zip', f'{param_dict["location"]}'),
        ('query', 'lunch'),
        ('radius', f'{param_dict["range"]}'),
    )

    async with app.http_session.get('https://wheelof.com/lunch/yelpProxyJSON.php', params=params) as r:
        r.raise_for_status()
        loc = get_random_lunch(await r.json())
        logger.info(f"location selected for {command['user_name']}: {loc}")
        return build_response_text(loc)


async def _get_slash_here_message(channel, slack, text):
    channel_members_response = await slack.query(methods.CONVERSATIONS_MEMBERS, data={'channel': channel})
    member_list = [f'<@{member}>' for member in channel_members_response['members']]
    message = f"{' '.join(member_list)}  {text}"
    return message


async def _can_here(channel, user_id, pg):
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
