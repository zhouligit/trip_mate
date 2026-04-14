from pydantic import BaseModel, Field


class WechatVerificationRequest(BaseModel):
    real_name: str = Field(min_length=1, max_length=32)
    id_no_last4: str = Field(min_length=4, max_length=4)


class IdcardVerificationRequest(BaseModel):
    id_number: str = Field(min_length=15, max_length=18)
    name: str = Field(min_length=1, max_length=32)
    ocr_image_url: str | None = Field(default=None, max_length=255)
