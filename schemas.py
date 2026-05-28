from typing import Optional
from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    status: str = "want_to_read"
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class BookUpdate(BaseModel):
    status: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    status: str
    rating: Optional[int]

    model_config = {"from_attributes": True}
