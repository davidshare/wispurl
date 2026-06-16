from pydantic import BaseModel, ConfigDict, Field


class TokenPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=32)
    token_type: str = "bearer"  # noqa: S105
    expires_in: int


class AccessTokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(min_length=1)
    token_type: str = "bearer"  # noqa: S105
    expires_in: int
