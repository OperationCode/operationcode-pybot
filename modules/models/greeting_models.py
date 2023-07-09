from pydantic import BaseModel, Field  # noqa: D100


class UserInfo(BaseModel):  # noqa: D101
    id: str = Field(  # noqa: A003
        ...,
        example="U02RK2AL5LZ",
        description="The Slack ID of the new user",
    )
    name: str = Field(
        ...,
        example="julio123",
        description="The Slack name of the new user",
    )
    first_name: str = Field(
        None,
        example="Julio",
        description="The first name of the new user",
    )
    last_name: str = Field(
        None,
        example="Mendez",
        description="The last name of the new user",
    )
    display_name: str = Field(
        None,
        example="julio123",
        description="The display name chosen by the user",
    )
    real_name: str = Field(
        None,
        example="Julio Mendez",
        description="The display name of the new user as entered by the user",
    )
    email: str = Field(..., example="test@example.com", description="Email of the user")
    zip_code: str = Field(None, example="12345", description="The zip code of the user")
    joined_date: str = Field(
        None,
        example="2013-01-30",
        description="The date the user joined the OC Slack",
    )
