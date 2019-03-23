import logging


class SlackMessageFilter(logging.Filter):
    def filter(self, record):
        return record.funcName != "_incoming_message"
