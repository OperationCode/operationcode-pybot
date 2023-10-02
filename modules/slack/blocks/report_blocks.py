from slack_sdk.models.blocks.basic_components import MarkdownTextObject, PlainTextObject  # noqa: D100
from slack_sdk.models.blocks.block_elements import ButtonElement, PlainTextInputElement
from slack_sdk.models.blocks.blocks import (
    ActionsBlock,
    HeaderBlock,
    InputBlock,
    SectionBlock,
)
from slack_sdk.models.views import View

from modules.airtable import message_text_table


def report_form_view_elements() -> View:  # noqa: D103
    title_text = PlainTextObject(text="OC Slack - Report", emoji=True)
    close_button_text = PlainTextObject(text="Cancel")
    submit_button_text = PlainTextObject(text="Submit Report")
    return View(
        type="modal",
        callback_id="report_form_submit",
        title=title_text,
        close=close_button_text,
        submit=submit_button_text,
        blocks=report_form_modal_blocks(),
        external_id="report_form_modal",
    )


def report_form_modal_blocks() -> list[SectionBlock | InputBlock]:
    """Return the blocks for the report form modal.

    :return: The blocks for the report form modal.
    """
    return [report_form_title_block(), report_form_input_block()]


def report_form_title_block() -> SectionBlock:  # noqa: D103
    text = MarkdownTextObject(
        text=":warning: Thank you for taking the time to report an issue to the moderation team. Please fill out the below input field with the text of the message you'd like to report. If you'd like, you can include a short description of why you are reporting it. The report will only be shown to the moderators of the OC Slack workspace.:warning:",  # noqa: E501
    )
    return SectionBlock(block_id="report_title_block", text=text)


def report_form_input_block() -> InputBlock:  # noqa: D103
    input_placeholder = PlainTextObject(
        text="You can copy and paste the text of the message you'd like to report or tell us a bit about what you are reporting...",  # noqa: E501
        emoji=True,
    )
    input_label = PlainTextObject(
        text="Text of message you are reporting or reason for your report*",
        emoji=True,
    )
    text_input = PlainTextInputElement(
        action_id="report_input_field",
        placeholder=input_placeholder,
        focus_on_load=True,
        multiline=True,
        min_length=2,
    )
    return InputBlock(block_id="report_input", element=text_input, label=input_label)


def report_claim_blocks(
    reporting_user_name: str,
    report_details: str,
) -> list[SectionBlock | HeaderBlock | ButtonElement]:
    """The blocks used for the report claim form.

    :param reporting_user_name: The username of the user who submitted the report.
    :param report_details: The details of the report.
    :return: The blocks for the report claim form.
    """  # noqa: D401
    return [
        report_claim_title_section(reporting_user_name),
        report_claim_details_header(),
        report_claim_details(report_details),
        report_claim_button(),
    ]


def report_claim_title_section(username: str) -> SectionBlock:  # noqa: D103
    text = MarkdownTextObject(
        text=f":warning: <@{username}> has submitted a report. :warning:",
    )
    return SectionBlock(text=text, block_id="report_claim_title")


def report_claim_details_header() -> HeaderBlock:  # noqa: D103
    text = PlainTextObject(text="Report details:", emoji=True)
    return HeaderBlock(block_id="report_claim_header", text=text)


def report_claim_details(report_details: str) -> SectionBlock:  # noqa: D103
    text = MarkdownTextObject(text=f"{report_details}")
    return SectionBlock(text=text, block_id="report_claim_details")


def report_claim_button() -> ActionsBlock:  # noqa: D103
    button_text = PlainTextObject(text="I Will Reach Out to Them")
    button_element = ButtonElement(
        text=button_text,
        style="primary",
        action_id="report_claim",
    )
    return ActionsBlock(block_id="report_claim_button", elements=[button_element])


def report_claim_claimed_button(claiming_username: str) -> ActionsBlock:  # noqa: D103
    button_text = PlainTextObject(text=f"Claimed by {claiming_username}!")
    button_element = ButtonElement(
        text=button_text,
        style="danger",
        action_id="reset_report_claim",
    )
    return ActionsBlock(block_id="report_claim_button", elements=[button_element])


def report_received_ephemeral_message() -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="report_received",
    )
    text = MarkdownTextObject(text=message_row.text)
    return SectionBlock(block_id="report_received", text=text)


def report_failed_ephemeral_message() -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="report_not_received",
    )
    text = MarkdownTextObject(text=message_row.text)
    return SectionBlock(block_id="report_not_received", text=text)
