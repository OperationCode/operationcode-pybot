"""
Block action payloads for testing Slack block-based interactions.
"""

import json
from enum import Enum


def make_mentor_request_blocks(
    service: str | None = None,
    skillsets: list[str] | None = None,
    details: str = "",
    affiliation: str | None = None,
) -> list[dict]:
    """Create a mentor request message blocks structure."""
    blocks = [
        # Block 0: Header
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Request a Mentor*"},
        },
        # Block 1: Description
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Fill out the form below to request a mentor."},
        },
        # Block 2: Service selector (BlockIndex.SERVICE)
        {
            "type": "section",
            "block_id": "service_block",
            "text": {"type": "mrkdwn", "text": "What do you need help with?"},
            "accessory": {
                "type": "static_select",
                "action_id": "mentor_service",
                "placeholder": {"type": "plain_text", "text": "Select a service"},
            },
        },
        # Block 3: Skillset selector (BlockIndex.SKILLSET)
        {
            "type": "section",
            "block_id": "skillset_block",
            "text": {"type": "mrkdwn", "text": "Select relevant skillsets:"},
            "accessory": {
                "type": "static_select",
                "action_id": "mentor_skillset",
                "placeholder": {"type": "plain_text", "text": "Select skillsets"},
            },
        },
        # Block 4: Selected skillsets display (BlockIndex.SELECTED_SKILLSETS)
        {
            "type": "section",
            "block_id": "selected_skillsets",
            "text": {"type": "mrkdwn", "text": "Selected skillsets:"},
        },
        # Block 5: Comments/details (BlockIndex.COMMENTS)
        {
            "type": "section",
            "block_id": "comments_block",
            "text": {"type": "mrkdwn", "text": "Additional details:"},
        },
        # Block 6: Affiliation selector (BlockIndex.AFFILIATION)
        {
            "type": "section",
            "block_id": "affiliation_block",
            "text": {"type": "mrkdwn", "text": "What is your affiliation?"},
            "accessory": {
                "type": "static_select",
                "action_id": "mentor_group",
                "placeholder": {"type": "plain_text", "text": "Select affiliation"},
            },
        },
        # Block 7: Mentor selector (optional)
        {
            "type": "section",
            "block_id": "mentor_block",
            "text": {"type": "mrkdwn", "text": "Request a specific mentor (optional):"},
            "accessory": {
                "type": "static_select",
                "action_id": "mentor_select",
                "placeholder": {"type": "plain_text", "text": "Select mentor"},
            },
        },
        # Block 8: Submit button (BlockIndex.SUBMIT)
        {
            "type": "actions",
            "block_id": "submit_block",
            "elements": [
                {
                    "type": "button",
                    "action_id": "mentor_submit",
                    "text": {"type": "plain_text", "text": "Submit Request"},
                    "style": "primary",
                },
                {
                    "type": "button",
                    "action_id": "clear_skillsets",
                    "text": {"type": "plain_text", "text": "Clear Skillsets"},
                },
            ],
        },
    ]

    # Add service if provided
    if service:
        blocks[2]["accessory"]["initial_option"] = {
            "text": {"type": "plain_text", "text": service},
            "value": service,
        }

    # Add skillsets if provided
    if skillsets:
        blocks[4]["fields"] = [{"type": "plain_text", "text": s, "emoji": True} for s in skillsets]

    # Add details if provided
    if details:
        blocks[5]["fields"] = [{"type": "plain_text", "text": details}]

    # Add affiliation if provided
    if affiliation:
        blocks[6]["accessory"]["initial_option"] = {
            "text": {"type": "plain_text", "text": affiliation},
            "value": affiliation,
        }

    return blocks


def make_mentor_request_action(
    user_id: str = "U123TEST",
    user_name: str = "testuser",
    channel_id: str = "C123CHANNEL",
    ts: str = "123456.789",
    service: str | None = None,
    skillsets: list[str] | None = None,
    details: str = "",
    affiliation: str | None = None,
    trigger_id: str = "trigger123",
    action_id: str = "mentor_submit",
    selected_option: dict | None = None,
) -> dict:
    """Create a full mentor request block action payload."""
    blocks = make_mentor_request_blocks(service, skillsets, details, affiliation)

    action = {
        "type": "block_actions",
        "user": {"id": user_id, "name": user_name},
        "channel": {"id": channel_id},
        "message": {"ts": ts, "blocks": blocks, "attachments": []},
        "trigger_id": trigger_id,
        "actions": [
            {
                "action_id": action_id,
                "block_id": "submit_block",
                "type": "button",
                "value": "submit",
            }
        ],
        "token": "supersecuretoken",
    }

    if selected_option:
        action["actions"][0]["selected_option"] = selected_option

    return action


def make_mentor_volunteer_blocks(skillsets: list[str] | None = None) -> list[dict]:
    """Create mentor volunteer form blocks."""
    skillset_text = " " if not skillsets else "\n".join(skillsets)

    return [
        # Block 0: Header
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Volunteer to be a Mentor*"},
        },
        # Block 1: Description
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select your areas of expertise below.",
            },
        },
        # Block 2: Skillset selector (VolunteerBlockIndex.SKILLSET_OPTIONS)
        {
            "type": "section",
            "block_id": "skillset_options",
            "text": {"type": "mrkdwn", "text": "Select your skillsets:"},
            "accessory": {
                "type": "static_select",
                "action_id": "volunteer_skillset",
                "placeholder": {"type": "plain_text", "text": "Add a skillset"},
                "options": [
                    {"text": {"type": "plain_text", "text": "Python"}, "value": "Python"},
                    {"text": {"type": "plain_text", "text": "JavaScript"}, "value": "JavaScript"},
                    {"text": {"type": "plain_text", "text": "DevOps"}, "value": "DevOps"},
                ],
            },
        },
        # Block 3: Selected skillsets (VolunteerBlockIndex.SELECTED_SKILLSETS)
        {
            "type": "section",
            "block_id": "selected_skillsets",
            "text": {"type": "mrkdwn", "text": "Your selected skillsets:"},
            "fields": [{"type": "plain_text", "text": skillset_text, "emoji": True}],
        },
        # Block 4: Divider
        {"type": "divider"},
        # Block 5: Submit button (VolunteerBlockIndex.SUBMIT)
        {
            "type": "actions",
            "block_id": "submit_block",
            "elements": [
                {
                    "type": "button",
                    "action_id": "volunteer_submit",
                    "text": {"type": "plain_text", "text": "Submit"},
                    "style": "primary",
                },
                {
                    "type": "button",
                    "action_id": "clear_volunteer_skillsets",
                    "text": {"type": "plain_text", "text": "Clear"},
                },
            ],
        },
    ]


def make_mentor_volunteer_action(
    user_id: str = "U123TEST",
    user_name: str = "testuser",
    channel_id: str = "C123CHANNEL",
    ts: str = "123456.789",
    skillsets: list[str] | None = None,
    action_id: str = "volunteer_submit",
    selected_option: dict | None = None,
) -> dict:
    """Create a mentor volunteer block action payload."""
    blocks = make_mentor_volunteer_blocks(skillsets)

    action = {
        "type": "block_actions",
        "user": {"id": user_id, "name": user_name},
        "channel": {"id": channel_id},
        "message": {"ts": ts, "blocks": blocks, "attachments": []},
        "trigger_id": "trigger123",
        "actions": [
            {
                "action_id": action_id,
                "block_id": "submit_block",
                "type": "button",
                "value": "submit",
            }
        ],
        "token": "supersecuretoken",
    }

    if selected_option:
        action["actions"][0]["selected_option"] = selected_option

    return action


# Zapier webhook payload for mentor requests
ZAPIER_MENTOR_REQUEST = {
    "record": "recABC123",
    "email": "requester@example.com",
    "service": "recSVC001",
    "skillsets": "Python,JavaScript",
    "affiliation": "Veteran",
    "details": "I need help with my Python project",
    "requested_mentor": None,
}

ZAPIER_MENTOR_REQUEST_WITH_MENTOR = {
    **ZAPIER_MENTOR_REQUEST,
    "requested_mentor": "recMENTOR001",
}


# Resource button actions for new members
def make_resource_button_action(
    user_id: str = "U123TEST",
    resource_id: str = "resource_1",
    channel_id: str = "C123CHANNEL",
) -> dict:
    """Create a resource button click action."""
    return {
        "type": "block_actions",
        "user": {"id": user_id, "name": "testuser"},
        "channel": {"id": channel_id},
        "message": {"ts": "123456.789", "blocks": []},
        "trigger_id": "trigger123",
        "actions": [
            {
                "action_id": "resource_btn",
                "block_id": "resources_block",
                "type": "button",
                "value": resource_id,
            }
        ],
        "token": "supersecuretoken",
    }


# Member greeted tracking action
def make_greeted_action(
    user_id: str = "U123GREETER",
    greeted_user_id: str = "U456NEWMEMBER",
    channel_id: str = "C123CHANNEL",
) -> dict:
    """Create a 'member greeted' tracking action."""
    return {
        "type": "block_actions",
        "user": {"id": user_id, "name": "greeter"},
        "channel": {"id": channel_id},
        "message": {"ts": "123456.789", "blocks": []},
        "trigger_id": "trigger123",
        "actions": [
            {
                "action_id": "greeted_btn",
                "block_id": "greeting_block",
                "type": "button",
                "value": greeted_user_id,
            }
        ],
        "token": "supersecuretoken",
    }


# Report message action
def make_report_message_action(
    reporter_id: str = "U123REPORTER",
    message_ts: str = "123456.789",
    channel_id: str = "C123CHANNEL",
) -> dict:
    """Create a report message action."""
    return {
        "type": "block_actions",
        "user": {"id": reporter_id, "name": "reporter"},
        "channel": {"id": channel_id},
        "message": {
            "ts": message_ts,
            "text": "This is the message being reported",
            "blocks": [],
        },
        "trigger_id": "trigger123",
        "actions": [
            {
                "action_id": "report_message",
                "block_id": "message_actions",
                "type": "button",
                "value": "report",
            }
        ],
        "token": "supersecuretoken",
    }


# Dialog submission for mentor details
def make_mentor_details_dialog_submission(
    user_id: str = "U123TEST",
    channel_id: str = "C123CHANNEL",
    ts: str = "123456.789",
    details: str = "My detailed request information",
) -> dict:
    """Create a dialog submission for mentor request details."""
    return {
        "type": "dialog_submission",
        "callback_id": "mentor_details",
        "user": {"id": user_id, "name": "testuser"},
        "channel": {"id": channel_id},
        "submission": {"details": details},
        "state": json.dumps({"channel": channel_id, "ts": ts}),
        "token": "supersecuretoken",
    }


# Report dialog submission
def make_report_dialog_submission(
    reporter_id: str = "U123REPORTER",
    reason: str = "Inappropriate content",
    message_link: str = "https://slack.com/archives/C123/p123456789",
) -> dict:
    """Create a dialog submission for message reports."""
    return {
        "type": "dialog_submission",
        "callback_id": "report_message",
        "user": {"id": reporter_id, "name": "reporter"},
        "submission": {"reason": reason, "message_link": message_link},
        "token": "supersecuretoken",
    }


# Claim mentee actions (legacy interactive_message format)
def make_claim_mentee_action(
    mentor_id: str = "U123MENTOR",
    record_id: str = "recABC123",
    is_claim: bool = True,
) -> dict:
    """Create a claim/unclaim mentee action."""
    return {
        "type": "interactive_message",
        "user": {"id": mentor_id},
        "actions": [
            {
                "name": record_id,
                "value": "mentee_claimed" if is_claim else "mentee_unclaimed",
            }
        ],
        "original_message": {
            "text": "Mentor request from <@U456>",
            "attachments": [
                {
                    "text": "Click to claim",
                    "callback_id": "claim_mentee",
                    "actions": [
                        {
                            "name": record_id,
                            "text": "Claim Mentee" if not is_claim else "Reset claim",
                            "type": "button",
                            "value": "mentee_unclaimed" if not is_claim else "reset_claim_mentee",
                        }
                    ],
                }
            ],
        },
        "channel": {"id": "C123MENTORS"},
        "message_ts": "123456.789",
        "callback_id": "claim_mentee",
        "token": "supersecuretoken",
    }


# Complete block action payloads as JSON strings (for form data)
class BlockActionPayload(Enum):
    """Pre-built block action payloads for testing."""

    MENTOR_REQUEST_SUBMIT = json.dumps(
        make_mentor_request_action(
            service="Resume Review",
            skillsets=["Python", "AWS"],
            details="Need help with my resume",
            affiliation="veteran",
        )
    )

    MENTOR_REQUEST_INCOMPLETE = json.dumps(
        make_mentor_request_action(
            service=None,
            skillsets=None,
            details="",
            affiliation=None,
        )
    )

    MENTOR_VOLUNTEER_SUBMIT = json.dumps(
        make_mentor_volunteer_action(skillsets=["Python", "JavaScript"])
    )

    MENTOR_VOLUNTEER_NO_SKILLSETS = json.dumps(make_mentor_volunteer_action(skillsets=None))

    CLAIM_MENTEE = json.dumps(make_claim_mentee_action(is_claim=True))

    UNCLAIM_MENTEE = json.dumps(make_claim_mentee_action(is_claim=False))
