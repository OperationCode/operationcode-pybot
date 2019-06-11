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


def mentor_request_attachments(services, mentors, skillsets):
    return [
        {
            "callback_id": "mentor_request_update",
            "fallback": "Mentor Request",
            "pretext": "Service (Required)",
            "actions": [
                {
                    "type": "select",
                    "text": "Service",
                    "name": "service",
                    "options": [
                        {"text": service, "value": service}
                        for service in sorted(services)
                    ],
                }
            ],
        },
        {
            "callback_id": "mentor_request_update",
            "pretext": "Mentor skillset",
            "fallback": "Mentor skillset",
            "actions": [
                {
                    "type": "select",
                    "text": "Skillset",
                    "name": "skillset",
                    "options": [
                        {"text": skillset, "value": skillset}
                        for skillset in sorted(skillsets)
                    ],
                },
                {
                    "type": "button",
                    "text": "Clear Skillsets",
                    "name": "clearSkills",
                    "value": "clearSkills",
                },
            ],
        },
        {
            "callback_id": "mentor_request_update",
            "pretext": "Select a specific mentor",
            "fallback": "Mentor Request",
            "actions": [
                {
                    "type": "select",
                    "text": "Specific Mentor",
                    "name": "mentor",
                    "options": [
                        {"text": mentor, "value": mentor} for mentor in sorted(mentors)
                    ],
                },
                {
                    "type": "button",
                    "text": "Clear Mentor",
                    "name": "clearMentor",
                    "value": "clearMentor",
                },
            ],
        },
        {
            "callback_id": "mentor_request_update",
            "pretext": "Additional Comments",
            "fallback": "Additional Comments",
            "actions": [
                {
                    "type": "button",
                    "text": "Add details",
                    "name": "addDetails",
                    "value": "addDetails",
                }
            ],
        },
        {
            "callback_id": "mentor_request_update",
            "pretext": "I certify that I am a member of the following group (Required)",
            "fallback": "Mentor Request",
            "actions": [
                {
                    "type": "select",
                    "name": "group",
                    "value": "",
                    "options": [
                        {"text": "Active Duty", "value": "Active Duty"},
                        {"text": "Military Spouse", "value": "Military Spouse"},
                        {"text": "Veteran", "value": "Veteran"},
                    ],
                }
            ],
        },
        {
            "callback_id": "mentor_request_submit",
            "fallback": "Mentor Request",
            "actions": [
                {
                    "type": "button",
                    "text": "Submit",
                    "name": "submit",
                    "value": "submit",
                    "style": "primary",
                },
                {
                    "type": "button",
                    "text": "Cancel",
                    "name": "cancel",
                    "value": "cancel",
                    "style": "danger",
                },
            ],
        },
    ]


def new_mentor_request_attachment(services, mentors, skillsets):
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
                    "action_id": "submit_btn",
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
