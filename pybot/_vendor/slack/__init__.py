"""
Vendored slack-sansio library for Python 3.12+
Original: https://github.com/pyslackers/slack-sansio
"""

from pybot._vendor.slack.methods import HOOK_URL, ROOT_URL
from pybot._vendor.slack.methods import Methods as methods

__all__ = ["methods", "HOOK_URL", "ROOT_URL"]
