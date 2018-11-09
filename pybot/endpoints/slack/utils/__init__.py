import os

from dotenv import load_dotenv

load_dotenv()

MENTOR_CHANNEL = os.environ.get("MENTOR_CHANNEL") or "G1DRT62UC"
COMMUNITY_CHANNEL = os.environ.get("COMMUNITY_CHANNEL") or "G12343"
MODERATOR_CHANNEL = os.environ.get('MODERATOR_CHANNEL') or 'G8NDRJJF9'
TICKET_CHANNEL = os.environ.get('TICKET_CHANNEL') or 'G8NDRJJF9'
APP_TOKEN = os.environ.get('APP_TOKEN') or "123"
YELP_TOKEN = os.environ.get('YELP_TOKEN') or 'token'
PYBACK_HOST = os.environ.get('PYBACK_HOST') or 'pyback'
PYBACK_PORT = os.environ.get('PYBACK_PORT') or 8000
PYBACK_TOKEN = os.environ.get('PYBACK_TOKEN') or 'token'
PORT = os.environ.get("SIRBOT_PORT", 5000)
HOST = os.environ.get("SIRBOT_ADDR", "0.0.0.0")

slack_configs = {
    'token': os.environ.get('BOT_OATH_TOKEN'),
    'verify': os.environ.get('VERIFICATION_TOKEN'),
    'bot_id': os.environ.get('SLACK_BOT_ID'),
    'bot_user_id': os.environ.get('SLACK_BOT_ID'),
}
