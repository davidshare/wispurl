from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SignupRequest(StrictModel):
    email: EmailStr = Field(max_length=320)
    password: SecretStr = Field(min_length=12, max_length=1024)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginRequest(StrictModel):
    email: EmailStr = Field(max_length=320)
    password: SecretStr = Field(min_length=1, max_length=1024)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class RefreshRequest(StrictModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class LogoutRequest(StrictModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class PublicUser(StrictModel):
    id: UUID
    email: EmailStr
