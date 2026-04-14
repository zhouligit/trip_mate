from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    group_id: int
