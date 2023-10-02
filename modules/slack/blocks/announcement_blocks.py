"""Slack blocks for the announcements in various channels."""
from slack_sdk.models.blocks.basic_components import MarkdownTextObject, PlainTextObject
from slack_sdk.models.blocks.blocks import HeaderBlock, SectionBlock


def general_announcement_blocks(
    header_text: str,
    text: str,
) -> list[HeaderBlock | SectionBlock]:
    """The blocks used for a general announcement.

    :param header_text: The text for the header.
    :param text: The text for the body.
    :return: A list of Header and Section blocks.
    """  # noqa: D401
    return [general_announcement_header(header_text), general_announcement_body(text)]


def general_announcement_header(header_text: str) -> HeaderBlock:
    """The header block for a general announcement.

    :param header_text: The text for the header.
    :return: The header block.
    """  # noqa: D401
    text = PlainTextObject(text="[" + header_text + "]", emoji=True)
    return HeaderBlock(block_id="general_announcement_header", text=text)


def general_announcement_body(text: str) -> SectionBlock:
    """The body block for a general announcement.

    :param text: The text for the body.
    :return: The body block.
    """  # noqa: D401
    text = MarkdownTextObject(text=text)
    return SectionBlock(text=text, block_id="general_announcement_body")
