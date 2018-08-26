import logging.config
import yaml
import os

from raven import setup_logging
from raven.handlers.logging import SentryHandler
from raven.processors import SanitizePasswordsProcessor
from sirbot.plugins.postgres import PgPlugin
from sirbot.plugins.slack import SlackPlugin
from dotenv import load_dotenv
from sirbot import SirBot
import raven

from pyback import endpoints
from pyback.plugins import AirtablePlugin

load_dotenv()
PORT = os.environ.get("SIRBOT_PORT", 5000)
HOST = os.environ.get("SIRBOT_ADDR", "127.0.0.1")
ACCESS_TOKEN = os.environ.get("OAUTH_ACCESS_TOKEN", "access token")
VERIFICATION_TOKEN = os.environ.get("VERIFICATION_TOKEN ", "verification token")
VERSION = "0.0.1"
LOG = logging.getLogger(__name__)


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
        LOG.exception(e)

    if "SENTRY_DSN" in os.environ:
        make_sentry_logger()

    bot = SirBot()

    slack = SlackPlugin()
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)

    airtable = AirtablePlugin()
    endpoints.airtable.create_endpoints(airtable)
    bot.load_plugin(airtable)

    if "POSTGRES_DSN" in os.environ:
        postgres = PgPlugin(
            version=VERSION,
            sql_migration_directory=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "../migrations"
            ),
            dsn=os.environ["POSTGRES_DSN"],
        )
        bot.load_plugin(postgres)

    bot.start(host=HOST, port=PORT, print=False)
