import asyncio
import logging

import aiohttp.web
from aiohttp.web import Response

from pybot._vendor.slack.actions import Action
from pybot._vendor.slack.commands import Command
from pybot._vendor.slack.events import Event
from pybot._vendor.slack.exceptions import (
    FailedVerification,
    InvalidSlackSignature,
    InvalidTimestamp,
)
from pybot._vendor.slack.sansio import validate_request_signature

LOG = logging.getLogger(__name__)


async def incoming_event(request):
    slack = request.app.plugins["slack"]
    payload = await request.json()
    LOG.log(5, "Incoming event payload: %s", payload)

    if payload.get("type") == "url_verification":
        if slack.signing_secret:
            try:
                raw_payload = await request.read()
                validate_request_signature(
                    raw_payload.decode("utf-8"), request.headers, slack.signing_secret
                )
                return Response(body=payload["challenge"])
            except (InvalidSlackSignature, InvalidTimestamp):
                return Response(status=500)
        elif payload["token"] == slack.verify:
            return Response(body=payload["challenge"])
        else:
            return Response(status=500)

    try:
        verification_token = await _validate_request(request, slack)
        event = Event.from_http(payload, verification_token=verification_token)
    except (FailedVerification, InvalidSlackSignature, InvalidTimestamp):
        return Response(status=401)

    if event["type"] == "message":
        return await _incoming_message(event, request)
    else:
        futures = list(_dispatch(slack.routers["event"], event, request.app))
        if futures:
            return await _wait_and_check_result(futures)

    return Response(status=200)


async def _incoming_message(event, request):
    slack = request.app.plugins["slack"]

    if slack.bot_id and (
        event.get("bot_id") == slack.bot_id
        or event.get("message", {}).get("bot_id") == slack.bot_id
    ):
        return Response(status=200)

    LOG.debug("Incoming message: %s", event)
    text = event.get("text")
    if slack.bot_user_id and text:
        mention = slack.bot_user_id in event["text"] or event["channel"].startswith("D")
    else:
        mention = False

    if mention and text and text.startswith(f"<@{slack.bot_user_id}>"):
        event["text"] = event["text"][len(f"<@{slack.bot_user_id}>") :]
        event["text"] = event["text"].strip()

    futures = []
    for handler, configuration in slack.routers["message"].dispatch(event):
        if configuration["mention"] and not mention:
            continue
        elif configuration["admin"] and event["user"] not in slack.admins:
            continue

        f = asyncio.ensure_future(handler(event, request.app))
        if configuration["wait"]:
            futures.append(f)
        else:
            f.add_done_callback(_callback)

    if futures:
        return await _wait_and_check_result(futures)

    return Response(status=200)


async def incoming_command(request):
    slack = request.app.plugins["slack"]
    payload = await request.post()

    try:
        verification_token = await _validate_request(request, slack)
        command = Command(payload, verification_token=verification_token)
    except (FailedVerification, InvalidSlackSignature, InvalidTimestamp):
        return Response(status=401)

    LOG.debug("Incoming command: %s", command)
    futures = list(_dispatch(slack.routers["command"], command, request.app))
    if futures:
        return await _wait_and_check_result(futures)

    return Response(status=200)


async def incoming_action(request):
    slack = request.app.plugins["slack"]
    payload = await request.post()
    LOG.log(5, "Incoming action payload: %s", payload)

    try:
        verification_token = await _validate_request(request, slack)
        action = Action.from_http(payload, verification_token=verification_token)
    except (FailedVerification, InvalidSlackSignature, InvalidTimestamp):
        return Response(status=401)

    LOG.debug("Incoming action: %s", action)

    futures = list(_dispatch(slack.routers["action"], action, request.app))
    if futures:
        return await _wait_and_check_result(futures)

    return Response(status=200)


def _callback(f):
    try:
        f.result()
    except Exception as e:
        LOG.exception(e)


def _dispatch(router, event, app):
    for handler, configuration in router.dispatch(event):
        f = asyncio.ensure_future(handler(event, app))
        if configuration["wait"]:
            yield f
        else:
            f.add_done_callback(_callback)


async def _wait_and_check_result(futures):
    dones, _ = await asyncio.wait(futures, return_when=asyncio.ALL_COMPLETED)
    try:
        results = [done.result() for done in dones]
    except Exception as e:
        LOG.exception(e)
        return Response(status=500)

    results = [result for result in results if isinstance(result, aiohttp.web.Response)]
    if len(results) > 1:
        LOG.warning("Multiple web.Response for handler, returning none")
    elif results:
        return results[0]

    return Response(status=200)


async def _validate_request(request, slack):
    if slack.signing_secret:
        raw_payload = await request.read()
        validate_request_signature(
            raw_payload.decode("utf-8"), request.headers, slack.signing_secret
        )
        return None
    else:
        return slack.verify
