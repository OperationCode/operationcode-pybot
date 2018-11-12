def ticket_dialog(clicker_email, text):
    return {
        'callback_id': 'open_ticket',
        'title': 'Open New Ticket',
        'submit_label': 'Submit',
        'elements': [
            {
                'type': 'text',
                'label': 'Email',
                'name': 'email',
                'subtype': 'email',
                'value': clicker_email

            },
            {
                'type': 'text',
                'label': 'Request Type',
                'name': 'type',
                'value': text
            },
            {
                'type': 'textarea',
                'label': 'Details',
                'name': 'details'
            }
        ]
    }


def mentor_request_attachments(services, mentors, skillsets):
    return [
        {
            'callback_id': 'mentor_request_update',
            "fallback": "Mentor Request",
            'pretext': 'Service (Required)',
            'actions': [
                {
                    'type': 'select', 'text': 'Service', 'name': 'service',
                    'options': [{'text': service, 'value': service} for service in services]
                }
            ]
        },
        {
            'callback_id': 'mentor_request_update',
            'pretext': 'Mentor skillset',
            "fallback": "Mentor skillset",
            'actions': [{
                'type': 'select', 'text': 'Skillset', 'name': 'skillset',
                'options': [{'text': skillset, 'value': skillset} for skillset in skillsets]
            },
                {
                    'type': 'button',
                    'text': 'Clear Skillsets',
                    'name': 'clearSkills',
                    'value': 'clearSkills',
                }
            ]
        },
        {
            'callback_id': 'mentor_request_update',
            'pretext': 'Select a specific mentor',
            'fallback': 'Mentor Request',
            'actions': [{
                'type': 'select', 'text': 'Specific Mentor', 'name': 'mentor',
                'options': [{'text': mentor, 'value': mentor} for mentor in mentors]
            }]
        },
        {
            'callback_id': 'mentor_request_update',
            'pretext': 'Additional Comments',
            'fallback': 'Additional Comments',
            'actions': [{
                'type': 'button',
                'text': 'Add details',
                'name': 'addDetails',
                'value': 'addDetails',
            }]
        },
        {
            'callback_id': 'mentor_request_update',
            'pretext': 'I certify that I am a member of the following group (Required)',
            "fallback": "Mentor Request",
            'actions': [{'type': 'select', 'name': 'group', 'value': '',
                         'options':
                             [
                                 {'text': 'Veteran', 'value': 'Veteran'},
                                 {'text': 'Active Duty', 'value': 'Active Duty'},
                                 {'text': 'Military Spouse', 'value': 'Military Spouse'},
                             ]
                         }]
        },
        {
            'callback_id': 'mentor_request_submit',
            "fallback": "Mentor Request",
            'actions': [
                {
                    'type': 'button',
                    'text': 'Submit',
                    'name': 'submit',
                    'value': 'submit',
                    'style': 'primary'
                },
                {
                    'type': 'button',
                    'text': 'Cancel',
                    'name': 'cancel',
                    'value': 'cancel',
                    'style': 'danger'
                },
            ]
        },
    ]
