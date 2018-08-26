import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RequestRouter:

    def __init__(self):
        self._routes = defaultdict(list)

    def register(self, request_type, handler, **detail):
        logger.info("Registering %s, %s to %s", request_type, detail, handler)
        self._routes[request_type].append(handler)

    def dispatch(self, request):
        logger.debug('Dispatching request "%s"', request.get("type"))
        if request["type"] in self._routes:
            for handler in self._routes.get(request['type']):
                yield handler
        else:
            return
