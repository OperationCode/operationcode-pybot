import logging  # noqa: D100

from slack_sdk.models.blocks.basic_components import (
    MarkdownTextObject,
    Option,
    PlainTextObject,
)
from slack_sdk.models.blocks.block_elements import (
    ButtonElement,
    PlainTextInputElement,
    StaticMultiSelectElement,
    StaticSelectElement,
)
from slack_sdk.models.blocks.blocks import ActionsBlock, Block, DividerBlock, InputBlock, SectionBlock
from slack_sdk.models.views import View

from modules.airtable import message_text_table
from modules.models.mentorship_models import (
    MentorshipAffiliation,
    MentorshipService,
    MentorshipSkillset,
)
from modules.slack.blocks import shared_blocks

logger = logging.getLogger(__name__)


def mentorship_request_view(  # noqa: D103
    services: list[MentorshipService],
    skillsets: list[MentorshipSkillset],
    affiliations: list[MentorshipAffiliation],
) -> View:
    logger.info("STAGE: Building mentorship request form view...")
    return View(
        type="modal",
        callback_id="mentorship_request_form_submit",
        title=PlainTextObject(text="OC Mentor Request", emoji=True),
        submit=PlainTextObject(text="Submit Request", emoji=True),
        cancel=PlainTextObject(text="Cancel", emoji=True),
        external_id="mentorship_request_form_modal",
        blocks=mentorship_request_blocks(services, skillsets, affiliations),
    )


def mentorship_request_blocks(
    services: list[MentorshipService],
    skillsets: list[MentorshipSkillset],
    affiliations: list[MentorshipAffiliation],
) -> list[SectionBlock | DividerBlock | InputBlock]:
    """The blocks used for the mentorship request form.

    :param services: The list of mentorship services.
    :param skillsets: The list of mentorship skillsets.
    :param affiliations: The affiliations of the requestor.
    :return: The blocks used for the mentorship request form.
    """  # noqa: D401
    logger.info("STAGE: Building the mentorship request blocks...")
    messages = message_text_table.retrieve_valid_messages_by_view(
        "Valid Mentorship Requests",
    )
    return [
        request_view_main_text(messages["mentorship_request_main"].text),
        shared_blocks.generic_divider_block(block_id="mentorship_request_divider_1"),
        request_view_services_input(
            services,
            messages["mentorship_request_service_label"].text,
            messages["mentorship_request_service_placeholder"].text,
        ),
        request_view_skillsets_input(
            skillsets,
            messages["mentorship_request_skillset_label"].text,
            messages["mentorship_request_skillset_placeholder"].text,
        ),
        request_view_details_input(
            messages["mentorship_request_details_label"].text,
            messages["mentorship_request_details_placeholder"].text,
        ),
        shared_blocks.generic_divider_block(block_id="mentorship_request_divider_2"),
        request_view_affiliations_input(
            affiliations,
            messages["mentorship_request_affiliation_label"].text,
            messages["mentorship_request_affiliation_placeholder"].text,
        ),
    ]


def request_view_main_text(main_text: str) -> SectionBlock:  # noqa: D103
    logger.info("STAGE: Building mentorship request form main section block...")
    return SectionBlock(
        block_id="mentorship_request_main_text",
        text=MarkdownTextObject(text=main_text),
    )


def request_view_services_input(  # noqa: D103
    services: list[MentorshipService],
    services_label: str,
    services_placeholder: str,
) -> InputBlock:
    logger.info("STAGE: Building mentorship request form services input block...")
    service_options = [Option(label=service.name, value=service.name) for service in services]
    input_element = StaticSelectElement(
        placeholder=PlainTextObject(text=services_placeholder, emoji=True),
        action_id="mentorship_service_selection",
        options=service_options,
    )
    return InputBlock(
        block_id="mentorship_service_input",
        label=PlainTextObject(text=services_label, emoji=True),
        element=input_element,
    )


def request_view_skillsets_input(  # noqa: D103
    skillsets: list[MentorshipSkillset],
    skillsets_label: str,
    skillsets_placeholder: str,
) -> InputBlock:
    logger.info("STAGE: Building mentorship request form skillsets input block...")
    service_options = [Option(label=skillset.name, value=skillset.name) for skillset in skillsets]
    input_element = StaticMultiSelectElement(
        placeholder=PlainTextObject(text=skillsets_placeholder, emoji=True),
        action_id="mentorship_skillset_multi_selection",
        options=service_options,
    )
    return InputBlock(
        block_id="mentor_skillset_input",
        label=PlainTextObject(text=skillsets_label, emoji=True),
        element=input_element,
    )


def request_view_details_input(  # noqa: D103
    details_label: str,
    details_placeholder: str,
) -> InputBlock:
    logger.info("STAGE: Building mentorship request form details input block...")
    input_element = PlainTextInputElement(
        action_id="details_text_input",
        multiline=True,
        min_length=10,
        placeholder=PlainTextObject(text=details_placeholder, emoji=True),
    )
    return InputBlock(
        block_id="details_input_block",
        label=PlainTextObject(text=details_label, emoji=True),
        element=input_element,
    )


def request_view_affiliations_input(  # noqa: D103
    affiliations: list[MentorshipAffiliation],
    affiliations_label: str,
    affiliations_placeholder: str,
) -> InputBlock:
    logger.info("STAGE: Building mentorship request form affiliations input block...")
    affiliation_options = [Option(label=affiliation.name, value=affiliation.name) for affiliation in affiliations]
    input_element = StaticSelectElement(
        placeholder=PlainTextObject(text=affiliations_placeholder, emoji=True),
        action_id="mentorship_affiliation_selection",
        options=affiliation_options,
    )
    return InputBlock(
        block_id="mentorship_affiliation_input",
        label=PlainTextObject(text=affiliations_label, emoji=True),
        element=input_element,
    )


def request_successful_block() -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_received_successfully",
    )
    return SectionBlock(
        block_id="mentorship_request_received_successfully",
        text=MarkdownTextObject(text=message_row.text),
    )


def request_unsuccessful_block() -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_unsuccessful",
    )
    return SectionBlock(
        block_id="mentorship_request_unsuccessful",
        text=MarkdownTextObject(text=message_row.text),
    )


def request_claim_blocks(  # noqa: D103
    requested_service: str,
    skillsets: list[str],
    affiliation: str,
    requesting_username: str,
) -> list[Block]:
    return [
        request_claim_service_block(requesting_username, requested_service),
        request_claim_skillset_block(skillsets),
        request_claim_affiliation_block(affiliation),
        request_claim_button(),
    ]


def request_claim_service_block(  # noqa: D103
    requesting_username: str,
    requested_service: str,
) -> SectionBlock:
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_claim_service_text",
    )
    return SectionBlock(
        block_id="mentorship_request_service_text",
        text=MarkdownTextObject(
            text=message_row.text.format(requesting_username, requested_service),
        ),
    )


def request_claim_skillset_block(skillsets: list[str]) -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_claim_skillset_text",
    )
    return SectionBlock(
        block_id="mentorship_request_skillset_text",
        text=MarkdownTextObject(text=message_row.text.format(", ".join(skillsets))),
    )


def request_claim_affiliation_block(affiliation: str) -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_claim_affiliation_text",
    )
    return SectionBlock(
        block_id="mentorship_request_affiliation_text",
        text=MarkdownTextObject(text=message_row.text.format(affiliation)),
    )


def request_claim_button() -> ActionsBlock:  # noqa: D103
    button_element = ButtonElement(
        text=PlainTextObject(text="Claim Mentorship Request", emoji=True),
        style="primary",
        action_id="claim_mentorship_request",
    )
    return ActionsBlock(block_id="claim_button_action_block", elements=[button_element])


def request_claim_reset_button(claiming_username: str) -> ActionsBlock:  # noqa: D103
    button_element = ButtonElement(
        text=PlainTextObject(
            text=f"Request Claimed By {claiming_username}",
            emoji=True,
        ),
        style="danger",
        action_id="reset_mentorship_request_claim",
    )
    return ActionsBlock(block_id="claim_button_action_block", elements=[button_element])


def request_claim_details_block(details: str) -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_claim_details_text",
    )
    return SectionBlock(
        block_id="mentorship_request_details_text",
        text=MarkdownTextObject(text=message_row.text.format(details)),
    )


def request_claim_tagged_users_block(usernames: list[str]) -> SectionBlock:  # noqa: D103
    message_row = message_text_table.retrieve_valid_message_row(
        message_slug="mentorship_request_claim_tagged_users",
    )
    return SectionBlock(
        block_id="mentorship_request_tagged_users",
        text=MarkdownTextObject(
            text=message_row.text.format(
                " ".join([f"<@{username}>" for username in usernames]),
            ),
        ),
    )
