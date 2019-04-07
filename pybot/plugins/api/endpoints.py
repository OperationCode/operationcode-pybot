import asyncio
import json
import logging

from aiohttp.web_response import Response

from pybot.plugins.api.request import SlackApiRequest

logger = logging.getLogger(__name__)


async def slack_api(request):
    api_plugin = request.app.plugins["api"]
    slack_request = SlackApiRequest.from_request(request)

    if not slack_request.authorized:
        logger.info(
            f"Received unauthorized request Request: {slack_request} Token: {slack_request.token}"
        )
        return Response(status=403)

    futures = list(_dispatch(api_plugin.routers["slack"], slack_request, request.app))

    if futures:
        return await _wait_and_check_result(futures)
    return Response(status=200)


def _dispatch(router, event, app):
    for handler, configuration in router.dispatch(event):
        f = asyncio.ensure_future(handler(event, app))
        yield f


async def _wait_and_check_result(futures):
    dones, _ = await asyncio.wait(futures, return_when=asyncio.ALL_COMPLETED)
    try:
        results = [done.result() for done in dones]
    except Exception as e:
        logger.exception(e)
        return Response(status=500)

    if len(results) > 1:
        logger.warning("Multiple web.Response for handler, returning none")

    elif results:
        result = (
            results[0]
            if isinstance(results[0], Response)
            else Response(body=json.dumps(results[0]))
        )

        return result
