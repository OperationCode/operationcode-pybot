from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ValidEnum(str, Enum):
    valid = "valid"
    invalid = "invalid"


class AirtableUser(BaseModel):
    id: str = Field(
        ...,
        example="usrAuExK7DEWFNiI6",
        description="Airtable provided unique ID of the user",
    )
    email: str = Field(..., example="test@example.com", description="Email of the user")
    name: str = Field(..., example="John Smith", description="Name of the user")


class AirtableRowBaseModel(BaseModel):
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
        description="Whether or not the record is valid - this is calculated on the Airtable table and has a value of valid if all fields are filled out",
    )
