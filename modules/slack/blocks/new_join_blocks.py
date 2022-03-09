from slack_sdk.models.blocks import (
    Block,
    SectionBlock,
    PlainTextObject,
    ButtonElement,
    MarkdownTextObject,
)

from modules.airtable import message_text_table


def new_join_immediate_welcome_blocks(joining_username: str) -> list[Block]:
    return [
        new_join_immediate_welcome_first_text(joining_username),
        new_join_immediate_welcome_second_text(),
        new_join_immediate_welcome_third_text(),
        new_join_immediate_welcome_fourth_text(),
        new_join_immediate_welcome_oc_homepage_button(),
        new_join_immediate_welcome_slack_download_button(),
        new_join_immediate_welcome_oc_coc_button(),
    ]


def new_join_delayed_welcome_blocks() -> list[Block]:
    return [
        new_join_delayed_welcome_first_text(),
        new_join_immediate_welcome_second_text(),
    ]


def new_join_immediate_welcome_first_text(joining_username: str) -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="new_member_join_immediate_welcome_first_text"
    )
    return SectionBlock(
        block_id="immediate_welcome_first_text",
        text=MarkdownTextObject(text=message_row.text.format(joining_username)),
    )


def new_join_immediate_welcome_second_text() -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="new_member_join_immediate_welcome_second_text"
    )
    return SectionBlock(
        block_id="immediate_welcome_second_text",
        text=MarkdownTextObject(text=message_row.text),
    )


def new_join_immediate_welcome_third_text() -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="new_member_join_immediate_welcome_third_text"
    )
    return SectionBlock(
        block_id="immediate_welcome_third_text",
        text=MarkdownTextObject(text=message_row.text),
    )


def new_join_immediate_welcome_fourth_text() -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="new_member_join_immediate_welcome_fourth_text"
    )
    return SectionBlock(
        block_id="immediate_welcome_fourth_text",
        text=MarkdownTextObject(text=message_row.text),
    )


def new_join_immediate_welcome_oc_homepage_button() -> SectionBlock:
    accessory = ButtonElement(
        text=PlainTextObject(text="OC Homepage", emoji=True),
        value="oc_home_page",
        url="https://operationcode.org/",
        action_id="oc_greeting_homepage_click",
        style="primary",
    )
    return SectionBlock(
        block_id="oc_homepage_button",
        text=MarkdownTextObject(text="Operation Code Homepage"),
        accessory=accessory,
    )


def new_join_immediate_welcome_slack_download_button() -> SectionBlock:
    accessory = ButtonElement(
        text=PlainTextObject(text="Slack Download", emoji=True),
        value="slack_download",
        url="https://slack.com/downloads/",
        action_id="oc_greeting_slack_download_click",
        style="primary",
    )
    return SectionBlock(
        block_id="slack_download_button",
        text=MarkdownTextObject(text="Slack Download"),
        accessory=accessory,
    )


def new_join_immediate_welcome_oc_coc_button() -> SectionBlock:
    accessory = ButtonElement(
        text=PlainTextObject(text="Operation Code CoC", emoji=True),
        value="operation_code_coc",
        url="https://github.com/OperationCode/community/blob/master/code_of_conduct.md",
        action_id="oc_greeting_coc_click",
        style="primary",
    )
    return SectionBlock(
        block_id="oc_coc_button",
        text=MarkdownTextObject(text="Operation Code CoC"),
        accessory=accessory,
    )


def new_join_delayed_welcome_first_text() -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="new_member_join_delayed_welcome_first_text"
    )
    return SectionBlock(
        block_id="delayed_welcome_first_text",
        text=MarkdownTextObject(text=message_row.text),
    )


def new_join_delayed_welcome_second_text() -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="new_member_join_delayed_welcome_second_text"
    )
    return SectionBlock(
        block_id="delayed_welcome_second_text",
        text=MarkdownTextObject(text=message_row.text),
    )
