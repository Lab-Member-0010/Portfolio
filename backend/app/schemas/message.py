from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MessageIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(default="", max_length=200)
    body: str = Field(min_length=5, max_length=5000)
    # honeypot: real users never fill this hidden field
    website: str = ""


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    subject: str
    body: str
    is_read: bool
    created_at: datetime


class MessageUpdate(BaseModel):
    is_read: bool
