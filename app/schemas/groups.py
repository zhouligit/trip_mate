from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    city_code: str = Field(min_length=1, max_length=32)
    target_count: int = Field(ge=30, le=100)
    threshold_count: int = Field(default=30, ge=30, le=50)


class StartVoteRequest(BaseModel):
    duration_hours: int = Field(default=24, ge=12, le=48)
