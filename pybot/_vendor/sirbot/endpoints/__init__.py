from aiohttp.web import json_response


async def plugins(request):
    data = [k for k in request.app["plugins"].keys()]
    return json_response({"plugins": data})
