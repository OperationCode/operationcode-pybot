from typing import Union

from slack_sdk.models.blocks.blocks import HeaderBlock, SectionBlock
from slack_sdk.models.blocks.basic_components import PlainTextObject, MarkdownTextObject


def general_announcement_blocks(
    header_text: str, text: str
) -> list[Union[HeaderBlock, SectionBlock]]:
    return [general_announcement_header(header_text), general_announcement_body(text)]


def general_announcement_header(header_text: str) -> HeaderBlock:
    text = PlainTextObject(text="[" + header_text + "]", emoji=True)
    return HeaderBlock(block_id="general_announcement_header", text=text)


def general_announcement_body(text: str) -> SectionBlock:
    text = MarkdownTextObject(text=text)
    return SectionBlock(text=text, block_id="general_announcement_body")
