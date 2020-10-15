"""Daily Programmer Bot package."""

import sys

if sys.version_info < (3, 6):
    raise ImportError("DailyProgrammerBot requires \
        Python 3.6+ because of slack API."
                      "<3")
