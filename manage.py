#!/usr/bin/env python
"""
Management commands for Pybot.

Usage:
    python manage.py replay-team-join <slack_user_id>
    python manage.py replay-team-join <slack_user_id> --skip-messages
    python manage.py replay-team-join <slack_user_id> --skip-backend
"""

import argparse
import asyncio
import logging
import os
import sys

import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def replay_team_join(
    user_id: str,
    skip_messages: bool = False,
    skip_backend: bool = False,
    skip_sleep: bool = True,
) -> None:
    """
    Replay the team_join workflow for a specific Slack user.

    This is useful for:
    - Testing the team_join flow after code changes
    - Re-linking a user to the backend after API changes
    - Debugging issues with the onboarding flow
    """
    from pybot._vendor.slack import methods
    from pybot._vendor.slack.io.aiohttp import SlackAPI
    from pybot.endpoints.slack.utils import (
        BACKEND_URL,
        COMMUNITY_CHANNEL,
        slack_configs,
    )
    from pybot.endpoints.slack.utils.event_utils import (
        build_messages,
        get_backend_auth_headers,
        link_backend_user,
        send_community_notification,
        send_user_greetings,
    )

    token = slack_configs.get("token")
    if not token:
        logger.error(
            "No Slack token configured. Set one of: "
            "BOT_USER_OAUTH_ACCESS_TOKEN, BOT_OAUTH_TOKEN, or SLACK_TOKEN"
        )
        sys.exit(1)

    logger.info(f"Starting team_join replay for user: {user_id}")
    logger.info(f"  Skip messages: {skip_messages}")
    logger.info(f"  Skip backend linking: {skip_backend}")
    logger.info(f"  Backend URL: {BACKEND_URL}")
    logger.info(f"  Community channel: {COMMUNITY_CHANNEL}")

    async with aiohttp.ClientSession() as session:
        slack_api = SlackAPI(session=session, token=token)

        # Verify the user exists
        try:
            user_info = await slack_api.query(methods.USERS_INFO, {"user": user_id})
            if not user_info.get("ok"):
                logger.error(f"Failed to fetch user info: {user_info.get('error')}")
                sys.exit(1)
            user_name = user_info["user"].get("real_name", user_info["user"].get("name"))
            user_email = user_info["user"]["profile"].get("email", "N/A")
            logger.info(f"  User found: {user_name} ({user_email})")
        except Exception as e:
            logger.error(f"Failed to fetch user info: {e}")
            sys.exit(1)

        # Build the welcome messages
        *user_messages, community_message, outreach_team_message = build_messages(user_id)

        if not skip_sleep:
            logger.info("Waiting 30 seconds (use --skip-sleep to bypass)...")
            await asyncio.sleep(30)

        # Send Slack messages
        if not skip_messages:
            logger.info("Sending welcome messages to user...")
            try:
                await send_user_greetings(user_messages, slack_api)
                logger.info("  User messages sent successfully")
            except Exception as e:
                logger.error(f"  Failed to send user messages: {e}")

            logger.info("Sending community notifications...")
            try:
                await send_community_notification(community_message, slack_api)
                await send_community_notification(outreach_team_message, slack_api)
                logger.info("  Community notifications sent successfully")
            except Exception as e:
                logger.error(f"  Failed to send community notifications: {e}")
        else:
            logger.info("Skipping Slack messages (--skip-messages)")

        # Link user to backend
        if not skip_backend:
            logger.info("Authenticating with backend API...")
            headers = await get_backend_auth_headers(session)
            if headers:
                logger.info("  Backend authentication successful")
                logger.info("Linking user to backend profile...")
                try:
                    await link_backend_user(user_id, headers, slack_api, session)
                    logger.info("  Backend user linking completed")
                except Exception as e:
                    logger.error(f"  Failed to link backend user: {e}")
            else:
                logger.error("  Backend authentication failed - check BACKEND_USERNAME/BACKEND_PASS")
        else:
            logger.info("Skipping backend linking (--skip-backend)")

    logger.info("Team join replay completed")


def main():
    parser = argparse.ArgumentParser(
        description="Pybot management commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Replay full team_join workflow for a user
  python manage.py replay-team-join U0A9K62QTL4

  # Only re-link user to backend (skip Slack messages)
  python manage.py replay-team-join U0A9K62QTL4 --skip-messages

  # Only send Slack messages (skip backend linking)
  python manage.py replay-team-join U0A9K62QTL4 --skip-backend

  # Include the 30-second delay (for realistic testing)
  python manage.py replay-team-join U0A9K62QTL4 --with-sleep
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # replay-team-join command
    replay_parser = subparsers.add_parser(
        "replay-team-join",
        help="Replay the team_join workflow for a specific user",
    )
    replay_parser.add_argument(
        "user_id",
        help="Slack user ID (e.g., U0A9K62QTL4)",
    )
    replay_parser.add_argument(
        "--skip-messages",
        action="store_true",
        help="Skip sending Slack messages (useful for just re-linking backend)",
    )
    replay_parser.add_argument(
        "--skip-backend",
        action="store_true",
        help="Skip backend user linking (useful for just re-sending messages)",
    )
    replay_parser.add_argument(
        "--with-sleep",
        action="store_true",
        help="Include the 30-second delay before sending messages",
    )
    replay_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if hasattr(args, "verbose") and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.command == "replay-team-join":
        asyncio.run(
            replay_team_join(
                user_id=args.user_id,
                skip_messages=args.skip_messages,
                skip_backend=args.skip_backend,
                skip_sleep=not args.with_sleep,
            )
        )


if __name__ == "__main__":
    main()
