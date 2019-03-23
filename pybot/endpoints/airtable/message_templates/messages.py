from typing import List


def mentor_request_text(user_id, service, skillsets, requested_mentor_message=None):
    if not skillsets:
        skillsets = "None provided"
    text = (
        f"User <@{user_id}> has requested a mentor for {service}\n\n"
        f"Requested Skillset(s): {skillsets.replace(',', ', ')}"
    )

    if requested_mentor_message:
        text += requested_mentor_message

    return text


def claim_mentee_attachment(record: str) -> List[dict]:
    return [
        {
            "text": "",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "claim_mentee",
            "attachment_type": "default",
            "actions": [
                {
                    "name": f"{record}",
                    "text": "Claim Mentee",
                    "type": "button",
                    "style": "primary",
                    "value": f"mentee_claimed",
                }
            ],
        }
    ]
