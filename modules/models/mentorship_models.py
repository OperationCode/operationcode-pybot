from datetime import datetime  # noqa: D100
from typing import Union

from pydantic import BaseModel, Field

from modules.models.shared_models import AirtableRowBaseModel


class MentorshipService(AirtableRowBaseModel):  # noqa: D101
    name: str = Field(
        ...,
        example="Pair Programming",
        description="Name of the service",
    )
    slug: str = Field(
        ...,
        example="pair_programming",
        description="Snake cased value for the service, used for identification and other purposes",
    )
    description: str = Field(
        ...,
        example="Work on a programming problem with a mentor while on a call",
        description="Description of the service",
    )


class MentorshipSkillset(AirtableRowBaseModel):  # noqa: D101
    name: str = Field(
        ...,
        example="Pair Programming",
        description="Name of the service",
    )
    slug: str = Field(
        ...,
        example="pair_programming",
        description="Snake cased value for the service, used for identification and other purposes",
    )
    mentors: list[str] = Field(
        None,
        example="['recoakW045JkGgQB7', 'rec9Un0YIvPsFjPZh', 'recnfnbHDZdie8jcD']",
        description="List of Airtable record IDs for mentors that have this skillset",
    )


class MentorshipAffiliation(AirtableRowBaseModel):  # noqa: D101
    name: str = Field(
        ...,
        example="US Veteran",
        description="The name of the affiliation",
    )
    slug: str = Field(
        ...,
        example="us_veteran",
        description="A more parseable slug for the affiliation, set by a formula in Airtable",
    )
    description: str = Field(
        ...,
        example="Veterans are former members of the United States military.",
        description="A short description of the affiliation",
    )


class Mentor(AirtableRowBaseModel):  # noqa: D101
    slack_name: str = Field(
        ...,
        example="john123",
        description="The Slack username for the mentor",
    )
    full_name: str = Field(
        ...,
        example="John Smith",
        description="The full name of the mentor",
    )
    email: str = Field(..., example="test@example.com", description="Email of the user")
    active: bool = Field(..., description="Whether or not the mentor is current active")
    skills: list[str] = Field(
        ...,
        example="['recoakW045JkGgQB7', 'rec9Un0YIvPsFjPZh', 'recnfnbHDZdie8jcD']",
        description="The Airtable provided IDs of the skillsets the mentor has added",
    )
    desired_mentorship_hours_per_week: int = Field(
        ...,
        description="The number of hours the mentor has specified they would like to mentor for",
    )
    time_zone: str = Field(
        ...,
        example="Indian/Maldives",
        description="The mentor's time zone",
    )
    max_mentees: int = Field(
        ...,
        description="The maximum number of mentees this mentor wants to work with at one time",
    )
    bio: str = Field(None, description="The self provided bio for the mentor")
    notes: str = Field(None, description="Any additional notes on the mentor")
    mentees_worked_with: list[str] = Field(
        None,
        example="['recCMMhN5j51NoagK']",
        description="The Airtable provided IDs of the mentees that the mentor has worked with, found on the Mentor Request table",  # noqa: E501
    )
    code_of_conduct_accepted: bool = Field(
        ...,
        description="Whether or not the mentor has accepted the code of conduct",
    )
    guidebook_read: bool = Field(
        ...,
        description="Whether or not the mentor has read the guidebook",
    )
    row_id: int = Field(..., description="Row ID from the Airtable table")


class MentorshipRequestBase(BaseModel):  # noqa: D101
    slack_name: str = Field(
        ...,
        example="john123",
        description="The Slack username for the user making the mentorship request",
    )
    email: str = Field(
        ...,
        example="test@example.com",
        description="Email of the requesting user",
    )
    service: str = Field(
        ...,
        example="Career Guidance",
        description="Service requested for the mentorship session",
    )
    additional_details: str = Field(
        ...,
        example="I need help with choosing a career path.",
        description="Details provided by the user making the request",
    )
    skillsets_requested: list[str] = Field(
        ...,
        example="['Go', 'React', 'Code Review']",
        description="List of all skillsets selected by the user making the request - this is used to match a mentor",
    )
    affiliation: str | list[str] = Field(
        ...,
        example="recCMMhN5j51NoagK",
        description="The Airtable created ID of a record on the Affiliations table",
    )
    claimed: bool = Field(
        False,  # noqa: FBT003
        description="Whether or not the mentor request has been claimed",
    )
    claimed_by: Union[str, list[str]] = Field(  # noqa: UP007
        None,
        description="The Airtable ID of the user who has claimed the request - this is pulled from the Mentor table",
    )
    claimed_on: datetime = Field(
        None,
        example="2021-04-23T10:20:30.400+00:00",
        description="ISO formatted UTC time when the request was claimed",
    )
    reset_by: str = Field(
        None,
        example="john123",
        description="Slack username of the user who reset the claim",
    )
    reset_on: datetime = Field(
        None,
        example="2021-04-23T10:20:30.400+00:00",
        description="ISO formatted UTC time when the request claim was reset",
    )
    reset_count: int = Field(
        0,
        description="The number of times the request claim was reset",
    )


class MentorshipRequest(MentorshipRequestBase, AirtableRowBaseModel):  # noqa: D101
    row_id: int = Field(
        None,
        description="The Airtable created row ID of the row, primarily used for sorting",
    )
    slack_message_ts: float = Field(
        ...,
        example=1640727458.000000,
        description="The message timestamp - this along with the channel ID allow the message to be found",
    )


class MentorshipRequestCreate(MentorshipRequestBase):
    """Create a new mentorship request."""
