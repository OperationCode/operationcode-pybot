import logging

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack import methods
from pybot._vendor.slack.events import Message

from .message_templates.tech import TechTerms
from .utils import BOT_URL

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_message(r".*", message_changed, subtype="message_changed")
    plugin.on_message(r".*", message_deleted, subtype="message_deleted")
    plugin.on_message(r".*\!tech", tech_tips)
    plugin.on_message(r".*\<\!here\>", here_bad)
    plugin.on_message(r".*\<\!channel\>", here_bad)
    plugin.on_message(r".*\!pybot", advertise_pybot)


def not_bot_message(event: Message):
    return (
        "message" not in event
        or "subtype" not in event["message"]
        or event["message"]["subtype"] != "bot_message"
    )


def not_bot_delete(event: Message):
    return "previous_message" in event and "bot_id" not in event["previous_message"]


async def advertise_pybot(event: Message, app: SirBot):
    response = dict(
        channel=event["channel"],
        text=f"OC-Community-Bot is a community led project\n <{BOT_URL}|source> ",
    )

    await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, data=response)


async def here_bad(event: Message, app: SirBot) -> None:
    if "channel_type" in event and event["channel_type"] != "im":
        user = event.get("user")
        user_id = f"<@{user}>" if user else "Hey you"
        await app.plugins["slack"].api.query(
            methods.CHAT_POST_MESSAGE,
            data=dict(
                channel=event["channel"],
                text=f"{user_id} - this had better be important!",
            ),
        )


async def tech_tips(event: Message, app: SirBot):
    if not_bot_message(event):
        logger.info(f"tech tips logging: {event}")
        try:
            tech_terms = await TechTerms(
                event["channel"], event["user"], event.get("text"), app
            ).grab_values()
            await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, tech_terms["message"])

        except Exception:
            logger.debug(f"Exception thrown while logging message_changed {event}")


async def message_changed(event: Message, app: SirBot):
    """
    Logs all message edits not made by a bot.
    """
    try:
        # need to check for bot_delete as deletes with replies that
        # result in a "tombstone" also send as edits
        if not_bot_message(event) and not_bot_delete(event):
            logger.info(
                f"CHANGE_LOGGING: edited: {event['ts']} for user: {event['previous_message']['user']}\n{event}"
            )
    except ValueError as e:
        logger.debug(
            f"Exception thrown while logging message_changed. Event: {event} || Error: {e}"
        )


async def message_deleted(event: Message, app: SirBot):
    """
    Logs all message deletions not made by a bot.
    """
    try:
        if not_bot_delete(event):
            logger.info(f"CHANGE_LOGGING: deleted: {event['ts']}\nEvent: {event}")
    except ValueError as e:
        logger.debug(
            f"Exception thrown while logging message_deleted. Event: {event} || Error: {e}"
        )
