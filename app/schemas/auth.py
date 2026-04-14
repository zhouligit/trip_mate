from pydantic import BaseModel, Field


class WechatLoginRequest(BaseModel):
    code: str = Field(min_length=2, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=255)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    profile_completed: bool
