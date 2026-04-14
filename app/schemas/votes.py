from pydantic import BaseModel


class CastVoteRequest(BaseModel):
    option_id: int
