import os
from pathlib import Path

from dotenv import load_dotenv

""" Loads values from .env file for local development """
url = Path(os.path.dirname(os.path.dirname(__file__))) / 'docker' / 'pybot.env'
load_dotenv(dotenv_path=url)
