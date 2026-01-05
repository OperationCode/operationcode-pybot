from pybot._vendor.slack import methods
from pybot.endpoints.slack.utils.slash_repeat import repeat_items


def get_slash_repeat_messages(user_id, channel, text):
    response_type = {
        "ephemeral": methods.CHAT_POST_EPHEMERAL,
        "message": methods.CHAT_POST_MESSAGE,
    }

    values_dict = repeat_items(text, user_id, channel)
    return response_type[values_dict["type"]], values_dict["message"]


def action_value(attachment):
    action = attachment["actions"][0]
    if "selected_options" in action:
        return action["selected_options"][0]["value"]
    return ""
