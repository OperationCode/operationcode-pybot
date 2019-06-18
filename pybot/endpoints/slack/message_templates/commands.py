from typing import List


def ticket_dialog(clicker_email, text):
    return {
        "callback_id": "open_ticket",
        "title": "Open New Ticket",
        "submit_label": "Submit",
        "elements": [
            {
                "type": "text",
                "label": "Email",
                "name": "email",
                "subtype": "email",
                "value": clicker_email,
            },
            {"type": "text", "label": "Request Type", "name": "type", "value": text},
            {"type": "textarea", "label": "Details", "name": "details"},
        ],
    }


def mentor_request_blocks(services, mentors, skillsets):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "👨‍🏫 Mentor Request Form 👩‍🏫\n"
                    "Thank you for signing up for a 30 minute mentoring session. Please fill out the form below"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "block_id": "mentor_service",
            "text": {"type": "mrkdwn", "text": "*Service (Required)*"},
            "accessory": {
                "action_id": "mentor_service_select",
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Service"},
                "options": [
                    {"text": {"type": "plain_text", "text": service}, "value": service}
                    for service in services
                ],
            },
        },
        {
            "type": "section",
            "block_id": "skillset",
            "text": {"type": "mrkdwn", "text": "*Mentor Skillsets*\n"},
            "accessory": {
                "type": "static_select",
                "action_id": "skillset_select",
                "placeholder": {"type": "plain_text", "text": "Skillset"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": skillset},
                        "value": skillset,
                    }
                    for skillset in skillsets
                ],
            },
        },
        {
            "type": "section",
            "block_id": "clear_skillsets",
            "text": {"type": "mrkdwn", "text": "*Selected Skillsets*"},
            "accessory": {
                "type": "button",
                "action_id": "clear_skillsets_btn",
                "text": {"type": "plain_text", "text": "Reset Skillsets"},
                "value": "reset_skillsets",
            },
        },
        {
            "type": "section",
            "block_id": "mentor",
            "text": {"type": "mrkdwn", "text": "*Select a specific mentor*"},
            "accessory": {
                "type": "static_select",
                "action_id": "mentor_select",
                "placeholder": {"type": "plain_text", "text": "Mentor"},
                "options": [
                    {"text": {"type": "plain_text", "text": mentor}, "value": mentor}
                    for mentor in mentors
                ],
            },
        },
        {
            "type": "section",
            "block_id": "comments",
            "text": {"type": "mrkdwn", "text": "*Add additional comments*"},
            "accessory": {
                "type": "button",
                "action_id": "comments_btn",
                "text": {"type": "plain_text", "text": "Add details"},
                "value": "addDetails",
            },
            "fields": [{"type": "plain_text", "text": " "}],
        },
        {
            "type": "section",
            "block_id": "affiliation",
            "text": {
                "type": "mrkdwn",
                "text": "*I certify that I am a member of the following group (Required)*",
            },
            "accessory": {
                "type": "static_select",
                "action_id": "affiliation_select",
                "placeholder": {"type": "plain_text", "text": "Military affiliation"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": "Veteran"},
                        "value": "Veteran",
                    },
                    {
                        "text": {"type": "plain_text", "text": "Active Duty"},
                        "value": "Active Duty",
                    },
                    {
                        "text": {"type": "plain_text", "text": "Military Spouse"},
                        "value": "Military Spouse",
                    },
                ],
            },
        },
        {"type": "divider"},
        {
            "type": "actions",
            "block_id": "submission",
            "elements": [
                {
                    "type": "button",
                    "action_id": "submit_mentor_btn",
                    "text": {"type": "plain_text", "text": "Submit"},
                    "style": "primary",
                    "value": "submit",
                },
                {
                    "type": "button",
                    "action_id": "cancel_btn",
                    "text": {"type": "plain_text", "text": "Cancel"},
                    "style": "danger",
                    "value": "cancel",
                },
            ],
        },
    ]


def mentor_volunteer_blocks(skillsets: List[str]) -> List[dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "Thank you for volunteering to be a mentor for the Operation Code community!  If you're looking "
                    "for the mentor request form, please use `/mentor` instead."
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "block_id": "volunteer_skillset",
            "text": {
                "type": "mrkdwn",
                "text": "*What area(s) are you interested in mentoring in?*",
            },
            "accessory": {
                "type": "static_select",
                "action_id": "skillset_select",
                "placeholder": {"type": "plain_text", "text": "Skillset"},
                "options": [
                    {
                        "text": {"type": "plain_text", "text": skillset},
                        "value": skillset,
                    }
                    for skillset in skillsets
                ],
            },
        },
        {
            "type": "section",
            "block_id": "clear_volunteer_skillsets",
            "text": {"type": "mrkdwn", "text": "*Selected Skillsets*"},
            "accessory": {
                "type": "button",
                "action_id": "clear_skillsets_btn",
                "text": {"type": "plain_text", "text": "Reset Skillsets"},
                "value": "reset_skillsets",
            },
        },
        {"type": "divider"},
        {
            "type": "actions",
            "block_id": "submission",
            "elements": [
                {
                    "type": "button",
                    "action_id": "submit_mentor_volunteer_btn",
                    "text": {"type": "plain_text", "text": "Submit"},
                    "style": "primary",
                    "value": "submit",
                },
                {
                    "type": "button",
                    "action_id": "cancel_btn",
                    "text": {"type": "plain_text", "text": "Cancel"},
                    "style": "danger",
                    "value": "cancel",
                },
            ],
        },
    ]
