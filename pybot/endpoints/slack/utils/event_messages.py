from typing import List


def team_join_initial_message(user_id: str) -> str:
    return (
        f"Hi <@{user_id}>,\n\n"
        "Welcome to Operation Code! I'm a bot designed to help answer questions and "
        "get you on your way in our community.\n\n "
        "Our goal here at Operation Code is to get veterans and their families started on the path to a career "
        "in programming. We do that through providing you with scholarships, mentoring, career development "
        "opportunities, conference tickets, and more!\n"
    )


def second_team_join_message() -> str:
    return (
        "Much of the provided aid requires veteran or military spouse status. Please verify your status on "
        "your profile at https://operationcode.org/ if you haven't already.\n\n"
        "You're currently in Slack, a chat application that serves as the hub of Operation Code. "
        "If you're visiting us via your browser, Slack provides a stand alone program to make staying in "
        "touch even more convenient.\n\n"
        "All active Operation Code projects are located on our source control repository. "
        "Our projects can be viewed on GitHub\n\n"
        "Lastly, please take a moment to review our Code of Conduct."
    )


def third_team_join_message() -> str:
    return f"If this is your first time using Slack, please watch this <https://youtu.be/m2JuAa6-ors|short tutorial> to get familiar with the app."


def delayed_team_join_message() -> str:
    return (
        f"Welcome to Operation Code's Slack Community, we're glad you're here! "
        f"Please share with us in #general what brings you to Operation Code, "
        f"and how we can assist you. Also, consider adding to your Operation Code "
        f"profile the links to your LinkedIn and GitHub accounts. "
        f"Lastly, consider connecting with us on our social media accounts: "
        f"<https://www.facebook.com/operationcode.org/|Facebook>, "
        f"<https://twitter.com/operation_code|Twitter>, "
        f"<https://business.linkedin.com/marketing-solutions/higher-education|LinkedIn>, "
        f"<https://www.instagram.com/operation_code/?hl=en|Instagram> and "
        f"<https://www.youtube.com/channel/UCAoJt4a_KEBmgXfoQUrNbSA/featured?view_as=public|YouTube>"
        f", and contribute to our open source platform on "
        f"<https://github.com/OperationCode|GitHub>. If you have any immediate needs, "
        f"please tag our @outreach-team in any public channel. "
    )


def external_button_attachments() -> List[dict]:
    return [
        {
            "text": "",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "external_buttons",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "github",
                    "text": "GitHub",
                    "type": "button",
                    "value": "github",
                    "url": "https://github.com/OperationCode",
                },
                {
                    "name": "download",
                    "text": "Slack Client",
                    "type": "button",
                    "value": "download",
                    "url": "https://slack.com/downloads",
                },
                {
                    "name": "code_of_conduct",
                    "text": "Code of Conduct",
                    "type": "button",
                    "value": "code_of_conduct",
                    "url": "https://github.com/OperationCode/community/blob/master/code_of_conduct.md",
                },
            ],
        }
    ]


def base_resources():
    return [
        {
            "text": "",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "resource_buttons",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "javascript",
                    "text": "JavaScript",
                    "type": "button",
                    "value": "javascript",
                },
                {
                    "name": "python",
                    "text": "Python",
                    "type": "button",
                    "value": "python",
                },
                {"name": "ruby", "text": "Ruby", "type": "button", "value": "ruby"},
            ],
        },
        {
            "text": "",
            "fallback": "",
            "color": "#3AA3E3",
            "callback_id": "suggestion",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "suggestion_button",
                    "text": "Are we missing something? Click!",
                    "type": "button",
                    "value": "suggestion_button",
                }
            ],
        },
    ]
