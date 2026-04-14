from pydantic import BaseModel, Field


class PersonalityAnswer(BaseModel):
    question_id: int
    option_id: int


class PersonalityTestRequest(BaseModel):
    answers: list[PersonalityAnswer] = Field(min_length=5, max_length=8)


class UpdateLocationRequest(BaseModel):
    city_code: str = Field(min_length=1, max_length=32)
    district_code: str | None = Field(default=None, max_length=32)
