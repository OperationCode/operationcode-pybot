from slack_sdk.models.blocks.blocks import SectionBlock, ActionsBlock
from slack_sdk.models.blocks.basic_components import MarkdownTextObject, PlainTextObject
from slack_sdk.models.blocks.block_elements import ButtonElement

from modules.models.greeting_models import UserInfo


def initial_greet_user_blocks(user_info: UserInfo) -> list:
    return [
        greeting_blocks_title(user_info.name),
        greeting_blocks_user_info(user_info),
        greeting_block_button(user_info.id),
    ]


def greeting_blocks_title(slack_name: str) -> SectionBlock:
    greeting_text = MarkdownTextObject(
        text=f"🎉 <@{slack_name}> has joined our community! 🎉"
    )
    return SectionBlock(block_id="title_text", text=greeting_text)


def greeting_blocks_user_info(user_info: UserInfo) -> SectionBlock:
    greeting_fields = []
    for key, value in user_info.__dict__.items():
        if key in ("zip_code", "email", "id"):
            pass
        elif value is None:
            pass
        else:
            greeting_fields.append(
                MarkdownTextObject(text=f"*{key.replace('_', ' ').title()}:*")
            )
            greeting_fields.append(MarkdownTextObject(text=f"{value}"))
    return SectionBlock(block_id="user_info", fields=greeting_fields)


def greeting_block_button(new_user_id: str) -> ActionsBlock:
    button_text = PlainTextObject(text="I will greet them!", emoji=True)
    greet_button = ButtonElement(
        text=button_text,
        action_id="greet_new_user_claim",
        style="primary",
        value=f"{new_user_id}",
    )
    return ActionsBlock(
        block_id="claim_action",
        elements=[greet_button],
    )


def greeting_block_claimed_button(claiming_user_name: str) -> ActionsBlock:
    """Creates an ActionsBlock that contains a button showing who claimed the greeting - this button allows anyone to reset the claim

    :param claiming_user_name: username of the user claiming the greeting
    :type claiming_user_name: str
    :return: an ActionsBlock with the claimed button that allows a reset
    :rtype: ActionsBlock
    """
    button_text = PlainTextObject(text=f"Greeted by {claiming_user_name}!")
    claimed_greet_button = ButtonElement(
        text=button_text,
        action_id="reset_greet_new_user_claim",
        style="danger",
        value=f"{claiming_user_name}",
    )
    return ActionsBlock(block_id="reset_claim_action", elements=[claimed_greet_button])
