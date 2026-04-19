from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    city_code: str = Field(min_length=1, max_length=32)
    # 联调阶段放宽人数校验；上线前可按 PRD 恢复 30–100 / 30–50
    target_count: int = Field(ge=1, le=10000)
    threshold_count: int = Field(default=30, ge=1, le=10000)


class StartVoteRequest(BaseModel):
    duration_hours: int = Field(default=24, ge=12, le=48)
