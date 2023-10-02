from slack_sdk.models.blocks import (  # noqa: D100
    ActionsBlock,
    Block,
    ButtonElement,
    DividerBlock,
    MarkdownTextObject,
    PlainTextObject,
    SectionBlock,
)

from modules.airtable import message_text_table


def generic_divider_block(block_id: str) -> DividerBlock:  # noqa: D103
    return DividerBlock(block_id=block_id)


def channel_join_request_successful_block(channel_name: str) -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="channel_join_request_successful",
    )
    return SectionBlock(
        block_id="channel_join_request_successful_block",
        text=MarkdownTextObject(text=message_row.text.format(channel_name)),
    )


def channel_join_request_unsuccessful_block() -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="channel_join_request_unsuccessful",
    )
    return SectionBlock(
        block_id="channel_join_request_unsuccessful_block",
        text=MarkdownTextObject(text=message_row.text),
    )


def channel_join_request_blocks(requesting_username: str) -> list[Block]:  # noqa: D103
    return [
        channel_join_request_main(requesting_username),
        channel_join_request_action(),
    ]


def channel_join_request_main(requesting_username: str) -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="channel_join_request_main_text",
    )
    return SectionBlock(
        block_id="request_main",
        text=MarkdownTextObject(text=message_row.text.format(requesting_username)),
    )


def channel_join_request_action() -> ActionsBlock:  # noqa: D103
    button_element = ButtonElement(
        text=PlainTextObject(text="I'll Invite Them!", emoji=True),
        style="primary",
        action_id="invite_to_channel_click",
    )
    return ActionsBlock(block_id="channel_invite_action", elements=[button_element])


def channel_join_request_reset_action(claiming_username: str) -> ActionsBlock:  # noqa: D103
    button_text = PlainTextObject(text=f"Invited by {claiming_username}!")
    button_element = ButtonElement(
        text=button_text,
        style="danger",
        action_id="reset_channel_invite",
    )
    return ActionsBlock(
        block_id="reset_channel_invite_action",
        elements=[button_element],
    )
