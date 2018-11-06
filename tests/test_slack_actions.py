from asynctest import CoroutineMock
from sirbot import SirBot


async def test_claim_mentee_response_attachment_is_list(action: dict, test_client, bot: SirBot):
    slack_mock = CoroutineMock(return_value={"user": {"profile": {"email": "email@email.com"}}})
    airtable_mock = CoroutineMock(return_value="U123")
    bot['plugins']['slack'].api.query = slack_mock
    bot['plugins']['airtable'].api.mentor_id_from_slack_email = airtable_mock
    bot['plugins']['airtable'].api.update_request = airtable_mock

    client = await test_client(bot)
    await client.post('/slack/actions', data=action)
    assert isinstance(slack_mock.call_args[0][1].event['attachments'], list)

