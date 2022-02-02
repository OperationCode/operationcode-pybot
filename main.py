import os

# import sys
# import yaml
# import json
# from slack_bolt.app import App
import re
import uvicorn
import logging
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, Body
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from modules.handlers.channel_join_handler import (
    handle_channel_join_request,
    handle_channel_join_request_claim,
    handle_channel_join_request_claim_reset,
)
from modules.handlers.mentorship_handler import (
    handle_mentor_request,
    handle_mentorship_request_form_submit,
    handle_mentorship_request_claim,
    handle_mentorship_request_claim_reset,
)
from modules.handlers.greeting_handler import (
    handle_new_member_join,
    handle_greeting_new_user_claim,
    handle_resetting_greeting_new_user_claim,
)
from modules.handlers.report_handler import (
    handle_report,
    handle_report_submit,
    handle_report_claim,
    handle_reset_report_claim,
)
from modules.handlers.daily_programmer import handle_daily_programmer_post
from modules.models.slack_models.event_models import (
    MemberJoinedChannelEvent,
    MessageReceivedChannelEvent,
)
from modules.models.slack_models.slack_models import (
    SlackResponseBody,
    SlackUserInfo,
)
from modules.models.slack_models.command_models import SlackCommandRequestBody
from modules.models.slack_models.view_models import SlackViewRequestBody
from modules.models.slack_models.action_models import SlackActionRequestBody
from modules.models.slack_models.shared_models import SlackTeam

load_dotenv()
logging.basicConfig(level=os.getenv("LOGGING_LEVEL", "INFO"))

logger = logging.getLogger(__name__)

# TODO: Add in /moderators slash command that lists the moderators pulled from Airtable
# TODO: Change mentorship view to dynamically add descriptions for the mentorship service block - will require dispatching an action on select and updating the block
# TODO: Allow matching mentor to mentee based on time zone, number of mentees a mentor already has (will need integration with Dreami to track long term relationships)
# TODO: Integrate with current backend to grab information about the mentee after a request is sent to allow for better matching (could be related to time zone, zip code, etc)
# TODO: On startup, check for mentor request threads that haven't been claimed that have been open for more than 24 hours - if there are any, tag @mentor-coordinators in the thread
# TODO: Related to the above TODO, spawn a job when a mentorship request is received to check to make sure it's been claimed in 24 hours - if not, ping @mentor-coordinators
# TODO: Evaluate the above TODOs and maybe decide on a job that checks twice a day? 10 AM CDT and 7 PM CDT? Use Airtable instead of threads to check
# TODO: Track view closures to see when people open and then close without submission
# TODO: Use discriminators and Unions to conditionally return different types depending on a particular field - see https://github.com/samuelcolvin/pydantic/issues/619
# TODO: Flush the cache using a webhook from Airtable when records are added or updated on various tables
# TODO: Check the membership of the mentors internal channel when linking for a mentorship request

# Start an asynchronous Slack Bolt application
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

# Currently, the app create functionality is not released in the Slack SDK for Python
#  see https://github.com/slackapi/python-slack-sdk/issues/1119
# try:
#     bot_name = os.getenv("BOT_NAME")
#     bot_username = os.getenv("BOT_USERNAME")
#     ngrok_url = os.getenv("NGROK_URL")
#     app_config_token = os.getenv("SLACK_APP_CONFIGURATION_TOKEN")
#     if bot_name is None or bot_username is None or ngrok_url is None or app_config_token is None:
#         raise "Please ensure you have all required environment variables set..."
#
#     synchronous_app = App(
#         token=os.environ.get("SLACK_BOT_TOKEN"),
#         signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
#     )
#     with open('bot_manifest.yml', 'r') as yaml_manifest:
#         yaml_obj = yaml.safe_load(yaml_manifest)
#         json_manifest = json.dumps(yaml_obj)
#         synchronous_app.client.apps_manifest_create(manifest=json_manifest)
#
# except Exception as generic_error:
#     sys.exit(1)

# Define the application handler for the async Slack Bolt application - this adapter is specific to FastAPI
app_handler = AsyncSlackRequestHandler(app)

# Define the API
api = FastAPI()

# Initialize an AsyncIOScheduler object to schedule tasks
Scheduler = AsyncIOScheduler({"apscheduler.timezone": "UTC"})
Trigger = IntervalTrigger(seconds=30)


# Start up our job scheduler on FastAPI startup and schedule jobs as needed
@api.on_event("startup")
async def startup_event() -> None:
    Scheduler.start()
    # job = Scheduler.add_job(schedule_messages, trigger=Trigger)
    # logging.debug(f"Scheduled {job.name} with job_id: {job.id}")


# On shutdown, shutdown the scheduler service first
@api.on_event("shutdown")
async def shutdown_event():
    await Scheduler.shutdown()


@api.post("/pybot/api/v1/slack/invite")
async def invite_new_user(
    email: str = Body(
        ..., example="Test@test.com", description="Email address of the user to invite"
    )
) -> None:
    await app.client.admin_users_invite(
        team_id=SlackTeam.slack_id,
        channel_ids=f"{SlackTeam.general_channel.id}",
        email=email,
    )


# The base URI for Slack to communicate with our application - this URI is used for events, commands, and any other interaction
@api.post("/slack/events")
async def base_endpoint(req: Request) -> Response:
    return await app_handler.handle(req)


@app.command("/mentor_request")
async def handle_mentor_request_command(
    context: AsyncBoltContext,
    body: dict[str, Any],
) -> None:
    logger.info("STAGE: Processing mentorship request...")
    await handle_mentor_request(SlackCommandRequestBody(**body), context)


@app.view("mentorship_request_form_submit")
async def handle_mentorship_request_form_view_submit(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing mentorship form submission...")
    await handle_mentorship_request_form_submit(SlackViewRequestBody(**body), context)


@app.action("claim_mentorship_request")
async def handle_mentorship_request_claim_click(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing a mentorship request claim...")
    await handle_mentorship_request_claim(SlackActionRequestBody(**body), context)


@app.action("reset_mentorship_request_claim")
async def handle_mentorship_request_claim_reset_click(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing a mentorship request claim reset...")
    await handle_mentorship_request_claim_reset(SlackActionRequestBody(**body), context)


@app.command("/new_join")
@app.event("member_joined_channel")
async def handle_new_member_join_event(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing new member joining...")
    if body["command"]:
        await handle_new_member_join(SlackCommandRequestBody(**body), context)
    else:
        await handle_new_member_join(MemberJoinedChannelEvent(**body), context)


@app.action("greet_new_user_claim")
async def handle_greeting_new_user_claim_action(
    context: AsyncBoltContext,
    body: dict[str, Any],
) -> None:
    logger.info("STAGE: Processing new claim on new user for greetings...")
    await handle_greeting_new_user_claim(SlackActionRequestBody(**body), context)


@app.action("reset_greet_new_user_claim")
async def handle_resetting_greeting_new_user_claim_action(
    context: AsyncBoltContext, body: dict[str, Any]
) -> None:
    logger.info("STAGE: Resetting claim on new user greeting...")
    await handle_resetting_greeting_new_user_claim(
        SlackActionRequestBody(**body), context
    )


@app.command("/report")
async def handle_report_command(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing report command...")
    await handle_report(body, context)


@app.view("report_form_submit")
async def handle_report_view_submit(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing report view submission...")
    await handle_report_submit(body, context)


@app.action("report_claim")
async def handle_report_claim_action(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing report claim....")
    await handle_report_claim(
        SlackResponseBody(**body, originating_user=SlackUserInfo(**body["user"])),
        context,
    )


@app.action("reset_report_claim")
async def handle_reset_report_claim_action(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Processing reset of report claim...")
    await handle_reset_report_claim(
        SlackResponseBody(**body, originating_user=SlackUserInfo(**body["user"])),
        context,
    )


@app.command("/join-pride")
@app.command("/join-blacks-in-tech")
async def handle_channel_join_request_command(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Handling channel join request...")
    await handle_channel_join_request(SlackCommandRequestBody(**body), context)


@app.action("invite_to_channel_click")
async def handle_invite_to_channel_click_action(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Handling invite button click for channel join...")
    await handle_channel_join_request_claim(SlackActionRequestBody(**body), context)


@app.action("reset_channel_invite")
async def handle_invite_to_channel_reset_action(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    logger.info("STAGE: Handling reset to invite button click for channel join...")
    await handle_channel_join_request_claim_reset(
        SlackActionRequestBody(**body), context
    )


@app.message(re.compile(r"(={2}.*={3})|(\[.*?])"))
async def handle_daily_programmer(
    body: dict[str, Any], context: AsyncBoltContext
) -> None:
    await handle_daily_programmer_post(MessageReceivedChannelEvent(**body), context)


if __name__ == "__main__":
    if os.environ.get("RUN_ENV") == "development":
        uvicorn.run(
            "main:api",
            host="0.0.0.0",
            port=8010,
            reload=True,
            reload_dirs=["./models", "./tests"],
        )
    else:
        # noinspection PyTypeChecker
        uvicorn.run("main:api", host="0.0.0.0", port=5001)
