from aiohttp.web_response import Response

from . import airtable, api, slack


async def handle_health_check(request):
    return Response(status=200)
