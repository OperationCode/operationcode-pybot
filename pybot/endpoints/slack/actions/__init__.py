from .general_actions import claimed, reset_claim
from .help_ticket import open_ticket, ticket_status
from .report_message import open_report_dialog, send_report
from .mentor_request import (
    mentor_request_submit,
    cancel_mentor_request,
    add_skillset,
    clear_skillsets,
    open_details_dialog,
    mentor_details_submit,
    claim_mentee,
    set_requested_mentor,
    set_requested_service,
    set_group,
)
from .new_member import (
    member_greeted,
    open_suggestion,
    post_suggestion,
    reset_greet,
    resource_buttons,
)


def create_endpoints(plugin):
    # simple actions that can be used in multiple scenarios
    plugin.on_action("claimed", claimed, name="claimed", wait=False)
    plugin.on_action("claimed", reset_claim, name="reset_claim", wait=False)

    # new member interactive actions
    plugin.on_action("resource_buttons", resource_buttons, wait=False)
    plugin.on_action("greeted", member_greeted, name="greeted", wait=False)
    plugin.on_action("greeted", reset_greet, name="reset_greet", wait=False)
    plugin.on_action("suggestion", open_suggestion, wait=False)
    plugin.on_action("suggestion_modal", post_suggestion, wait=False)

    # reporting related interactive actions
    plugin.on_action("report_message", open_report_dialog, wait=False)
    plugin.on_action("report_dialog", send_report, wait=False)

    # help ticket/request interactive actions
    plugin.on_action("open_ticket", open_ticket, wait=False)
    plugin.on_action("ticket_status", ticket_status, wait=False)

    # mentorship related interactive actions
    plugin.on_action(
        "mentor_request_submit", mentor_request_submit, name="submit", wait=False
    )
    plugin.on_action(
        "mentor_request_submit", cancel_mentor_request, name="cancel", wait=False
    )

    # plugin.on_action("mentor_request_update", mentor_request_update, wait=False)
    plugin.on_action("mentor_request_update", add_skillset, name="skillset", wait=False)
    plugin.on_action(
        "mentor_request_update", clear_skillsets, name="clearSkills", wait=False
    )
    plugin.on_action(
        "mentor_request_update", open_details_dialog, name="addDetails", wait=False
    )
    plugin.on_action(
        "mentor_request_update", set_requested_mentor, name="mentor", wait=False
    )
    plugin.on_action(
        "mentor_request_update", set_requested_service, name="service", wait=False
    )
    plugin.on_action("mentor_request_update", set_group, name="group", wait=False)

    plugin.on_action("mentor_details_submit", mentor_details_submit, wait=False)
    plugin.on_action("claim_mentee", claim_mentee, wait=False)
    plugin.on_action("reset_claim_mentee", claim_mentee, wait=False)
