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
                "value": clicker_email

            },
            {
                "type": "text",
                "label": "Request Type",
                "name": "type",
                "value": text
            },
            {
                "type": "textarea",
                "label": "Details",
                "name": "details"
            }
        ]
    }
