import os

from dotenv import load_dotenv

load_dotenv()

COMMUNITY_CHANNEL = os.environ.get("COMMUNITY_CHANNEL") or "G12343"
