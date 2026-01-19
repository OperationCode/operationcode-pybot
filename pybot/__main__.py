import logging.config
import os

import yaml

from pybot._vendor.sirbot import SirBot
from pybot._vendor.sirbot.plugins.slack import SlackPlugin
from pybot.endpoints import handle_health_check
from pybot.endpoints.slack.utils import HOST, PORT, slack_configs
from pybot.sentry import init_sentry

from . import endpoints
from .plugins import AirtablePlugin, APIPlugin

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../logging.yml")
        ) as log_configfile:
            logging.config.dictConfig(yaml.load(log_configfile.read(), Loader=yaml.SafeLoader))
    except Exception as e:
        logging.basicConfig(level=logging.DEBUG)
        logger.exception(e)

    init_sentry()

    bot = SirBot()

    slack = SlackPlugin(**slack_configs)
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)

    admin_configs = dict(**slack_configs)
    admin_token = os.environ.get("APP_ADMIN_OAUTH_TOKEN", "FAKE_ADMIN_TOKEN")
    if admin_token:
        admin_configs["token"] = admin_token
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
