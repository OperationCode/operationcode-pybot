"""Main program."""
import os
from bot import DailyProgrammerBot


def main():
    """Run main program."""
    app = DailyProgrammerBot()
    app.start(port=int(os.environ.get("PORT", 3000)))


if __name__ == "__main__":
    """Catch main function."""
    main()
