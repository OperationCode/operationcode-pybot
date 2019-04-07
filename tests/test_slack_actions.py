from asynctest import CoroutineMock
from sirbot import SirBot


async def test_claim_mentee_response_attachment_is_list(
    action: dict, aiohttp_client, bot: SirBot
):
    client, slack_mock = await create_mocks(aiohttp_client, bot)

    await client.post("/slack/actions", data=action)
    assert isinstance(slack_mock.call_args[0][1]["attachments"], list)


async def test_claim_mentee_response_contains_original_text(
    action: dict, aiohttp_client, bot: SirBot
):
    client, slack_mock = await create_mocks(aiohttp_client, bot)
    await client.post("/slack/actions", data=action)
    request_payload = slack_mock.call_args[0][1]
    assert request_payload["text"] is not None


async def create_mocks(aiohttp_client, bot):
    slack_mock = CoroutineMock(
        return_value={"user": {"profile": {"email": "email@email.com"}}}
    )
    airtable_mock = CoroutineMock(return_value="U123")
    bot["plugins"]["slack"].api.query = slack_mock
    bot["plugins"]["airtable"].api.find_records = CoroutineMock(return_value=[])
    bot["plugins"]["airtable"].api.update_request = airtable_mock
    bot["plugins"]["airtable"].api.get_name_from_record_id = airtable_mock
    bot["plugins"]["airtable"].api.get_row_from_record_id = airtable_mock
    client = await aiohttp_client(bot)
    return client, slack_mock
