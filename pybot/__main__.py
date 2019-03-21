import os
import yaml
import logging.config
from aiohttp.web_response import Response
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from raven.processors import SanitizePasswordsProcessor
from sirbot.plugins.slack import SlackPlugin
from sirbot import SirBot
import raven

from . import endpoints
from .plugins import AirtablePlugin
from pybot.endpoints.slack.utils import PORT, HOST
from pybot.endpoints.slack.utils import slack_configs

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
            logging.config.dictConfig(yaml.load(log_configfile.read()))
    except Exception as e:
        logging.basicConfig(level=logging.DEBUG)
        logger.exception(e)

    if "SENTRY_DSN" in os.environ:
        make_sentry_logger()

    bot = SirBot()

    slack = SlackPlugin(**slack_configs)
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)

    airtable = AirtablePlugin()
    endpoints.airtable.create_endpoints(airtable)
    bot.load_plugin(airtable)

    # Add route to respond to AWS health check
    bot.router.add_get("/health", lambda request: Response(status=200))
    logging.getLogger('aiohttp.access').setLevel(logging.WARNING)

    bot.start(host=HOST, port=PORT, print=logger.info)
