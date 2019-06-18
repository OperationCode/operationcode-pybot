import logging.config
import os

import raven
import yaml
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from raven.processors import SanitizePasswordsProcessor
from sirbot import SirBot
from sirbot.plugins.slack import SlackPlugin

from pybot.endpoints import handle_health_check
from pybot.endpoints.slack.utils import HOST, PORT, slack_configs

from . import endpoints
from .plugins import AirtablePlugin, APIPlugin

VERSION = "1.0"
logger = logging.getLogger(__name__)


def make_sentry_logger():
    client = raven.Client(
        dsn=os.environ["SENTRY_DSN"],
        release=VERSION,
        processor=SanitizePasswordsProcessor,
    )
    handler = SentryHandler(client)
    handler.setLevel(logging.WARNING)
    setup_logging(handler)


if __name__ == "__main__":
    try:
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../logging.yml")
        ) as log_configfile:
            logging.config.dictConfig(
                yaml.load(log_configfile.read(), Loader=yaml.SafeLoader)
            )
    except Exception as e:
        logging.basicConfig(level=logging.DEBUG)
        logger.exception(e)

    if "SENTRY_DSN" in os.environ:
        make_sentry_logger()

    bot = SirBot()

    slack = SlackPlugin(**slack_configs)
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)

    admin_configs = dict(**slack_configs)
    admin_configs["token"] = os.environ.get("APP_ADMIN_OAUTH_TOKEN")
    admin_slack = SlackPlugin(**admin_configs)
    bot.load_plugin(admin_slack, name="admin_slack")

    airtable = AirtablePlugin()
    endpoints.airtable.create_endpoints(airtable)
    bot.load_plugin(airtable)

    api_plugin = APIPlugin()
    endpoints.api.create_endpoints(api_plugin)
    bot.load_plugin(api_plugin)

    # Add route to respond to AWS health check
    bot.router.add_get("/health", handle_health_check)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    bot.start(host=HOST, port=PORT, print=logger.info)
