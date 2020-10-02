import os

BOT_USER_OAUTH_ACCESS_TOKEN = os.environ.get("BOT_USER_OAUTH_ACCESS_TOKEN")
BOT_OAUTH_TOKEN = os.environ.get("BOT_OAUTH_TOKEN")
BOT_OATH_TOKEN = os.environ.get("BOT_OATH_TOKEN")
MENTOR_CHANNEL = os.environ.get("MENTOR_CHANNEL", "mentors-internal")
COMMUNITY_CHANNEL = os.environ.get("COMMUNITY_CHANNEL", "greetings")
MODERATOR_CHANNEL = os.environ.get("MODERATOR_CHANNEL", "moderators")
OPS_CHANNEL = os.environ.get("OPS_CHANNEL", "oc-ops")
SLACK_BOT_USER_ID = os.environ.get("SLACK_BOT_USER_ID", "ABC123")
SLACK_BOT_ID = os.environ.get("SLACK_BOT_ID", "ABC123")
YELP_TOKEN = os.environ.get("YELP_TOKEN", "token")
PORT = os.environ.get("SIRBOT_PORT", 5000)
HOST = os.environ.get("SIRBOT_ADDR", "0.0.0.0")
PYBOT_ENV = os.environ.get("PYBOT_ENV", "dev")
BACKEND_URL = os.environ.get("BACKEND_URL", "https://api.operationcode.org")
BACKEND_USERNAME = os.environ.get("BACKEND_USERNAME", "Pybot@test.test")
BACKEND_PASS = os.environ.get("BACKEND_PASS", "fakePassword")

BOT_URL = "https://github.com/OperationCode/operationcode-pybot"

slack_configs = {
    "token": BOT_USER_OAUTH_ACCESS_TOKEN
    or BOT_OAUTH_TOKEN
    or BOT_OATH_TOKEN,  # fallback for old values
    "signing_secret": os.environ.get("SLACK_BOT_SIGNING_SECRET"),
    "verify": os.environ.get("VERIFICATION_TOKEN"),
    "bot_id": SLACK_BOT_ID,
    "bot_user_id": SLACK_BOT_USER_ID,
}
