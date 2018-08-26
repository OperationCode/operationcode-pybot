import asyncio
import logging

from aiohttp.web_response import Response

logger = logging.getLogger(__name__)


async def incoming_request(request):
    airtable = request.app.plugins['airtable']
    payload = await request.json()
    logger.debug('Incoming event payload: %s', payload)

    futures = list(_dispatch(airtable.routers['request'], payload, request.app))
    if futures:
        return await _wait_and_check_result(futures)
    return Response(status=200)


def _dispatch(router, event, app):
    for handler, configuration in router.dispatch(event):
        f = asyncio.ensure_future(handler(event, app))
        if configuration['wait']:
            yield f
        else:
            f.add_done_callback(_callback)


def _callback(f):
    try:
        f.result()
    except Exception as e:
        logger.exception(e)


async def _wait_and_check_result(futures):
    dones, _ = await asyncio.wait(futures, return_when=asyncio.ALL_COMPLETED)
    try:
        results = [done.result() for done in dones]
    except Exception as e:
        logger.exception(e)
        return Response(status=500)

    results = [result for result in results if isinstance(result, Response)]
    if len(results) > 1:
        logger.warning('Multiple web.Response for handler, returning none')
    elif results:
        return results[0]

    return Response(status=200)
