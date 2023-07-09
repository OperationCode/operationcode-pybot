"""Shared models for Airtable tables."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ValidEnum(str, Enum):
    """Enum for valid and invalid."""

    valid = "valid"
    invalid = "invalid"


class AirtableUser(BaseModel):
    """Model for Airtable user."""

    id: str = Field(  # noqa: A003
        ...,
        example="usrAuExK7DEWFNiI6",
        description="Airtable provided unique ID of the user",
    )
    email: str = Field(..., example="test@example.com", description="Email of the user")
    name: str = Field(..., example="John Smith", description="Name of the user")


class AirtableRowBaseModel(BaseModel):
    """Base model for Airtable rows."""

    airtable_id: str = Field(
        ...,
        example="rec8CRVRJOKYBIDIL",
        description="Airtable provided unique ID for the row",
    )
    created_at: datetime = Field(
        ...,
        example="2021-04-23T10:20:30.400+00:00",
        description="When the Airtable record was created",
    )
    last_modified: datetime = Field(
        None,
        example="2021-04-23T10:20:30.400+00:00",
        description="When the Airtable record was last updated",
    )
    last_modified_by: AirtableUser = Field(
        None,
        example="JulioMendez",
        description="Name of the user who last modified the Airtable record",
    )
    valid: ValidEnum = Field(
        None,
        example="invalid",
        description="Whether or not the record is valid - this is calculated on the Airtable table and has a value of valid if all fields are filled out",  # noqa: E501
    )
