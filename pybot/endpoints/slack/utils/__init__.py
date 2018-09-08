import os

from dotenv import load_dotenv

load_dotenv()

COMMUNITY_CHANNEL = os.environ.get("COMMUNITY_CHANNEL") or "G12343"
APP_TOKEN = os.environ.get('APP_TOKEN') or "123"
PYBACK_HOST = os.environ.get('PYBACK_HOST') or 'pyback'
PYBACK_PORT = os.environ.get('PYBACK_PORT') or 8000
PYBACK_TOKEN = os.environ.get('PYBACK_TOKEN') or 'token'
