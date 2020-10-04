from sirbot.plugins.slack import SlackPlugin

from .general_actions import claimed, delete_message, reset_claim
from .mentor_request import (
    add_skillset,
    claim_mentee,
    clear_mentor,
    clear_skillsets,
    mentor_details_submit,
    mentor_request_submit,
    open_details_dialog,
    set_group,
    set_requested_mentor,
    set_requested_service,
)
from .mentor_volunteer import (
    add_volunteer_skillset,
    clear_volunteer_skillsets,
    submit_mentor_volunteer,
)
from .new_member import (
    member_greeted,
    open_suggestion,
    post_suggestion,
    reset_greet,
    resource_buttons,
)
from .report_message import open_report_dialog, send_report


def create_endpoints(plugin: SlackPlugin):
    # simple actions that can be used in multiple scenarios
    plugin.on_action("claimed", claimed, name="claimed", wait=False)
    plugin.on_action("claimed", reset_claim, name="reset_claim", wait=False)
    plugin.on_block("submission", delete_message, action_id="cancel_btn", wait=False)

    # new member interactive actions
    plugin.on_action("resource_buttons", resource_buttons, wait=False)
    plugin.on_action("greeted", member_greeted, name="greeted", wait=False)
    plugin.on_action("greeted", reset_greet, name="reset_greet", wait=False)
    plugin.on_action("suggestion", open_suggestion, wait=False)
    plugin.on_action("suggestion_modal", post_suggestion, wait=False)

    # reporting related interactive actions
    plugin.on_action("report_message", open_report_dialog, wait=False)
    plugin.on_action("report_dialog", send_report, wait=False)

    # mentorship related interactive actions
    plugin.on_block(
        "mentor_service",
        set_requested_service,
        wait=False,
        action_id="mentor_service_select",
    )
    plugin.on_block("skillset", add_skillset, action_id="skillset_select", wait=False)
    plugin.on_block(
        "clear_skillsets", clear_skillsets, action_id="clear_skillsets_btn", wait=False
    )
    plugin.on_block(
        "mentor", set_requested_mentor, action_id="mentor_select", wait=False
    )
    plugin.on_block(
        "comments", open_details_dialog, action_id="comments_btn", wait=False
    )
    plugin.on_block("mentor_details_submit", mentor_details_submit, wait=False)
    plugin.on_block(
        "affiliation", set_group, action_id="affiliation_select", wait=False
    )
    plugin.on_block(
        "submission", mentor_request_submit, action_id="submit_mentor_btn", wait=False
    )

    # mentor volunteer actions
    plugin.on_block("volunteer_skillset", add_volunteer_skillset, wait=False)
    plugin.on_block("clear_volunteer_skillsets", clear_volunteer_skillsets, wait=False)
    plugin.on_block(
        "submission",
        submit_mentor_volunteer,
        action_id="submit_mentor_volunteer_btn",
        wait=False,
    )

    # mentorship claims
    plugin.on_action("claim_mentee", claim_mentee, wait=False)
    plugin.on_action("reset_claim_mentee", claim_mentee, wait=False)
