from pydantic import BaseModel, Field


class AddFriendRequest(BaseModel):
    target_user_id: int = Field(gt=0)
