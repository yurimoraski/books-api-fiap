from pydantic import BaseModel
from typing import Optional


class BookBase(BaseModel):
    title: str
    price: float
    rating: int
    availability: int
    category: str
    image_url: Optional[str] = None
    product_page_url: Optional[str] = None
    description: Optional[str] = None
    upc: Optional[str] = None


class BookOut(BookBase):
    id: int

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    name: str
    count: int


class HealthOut(BaseModel):
    status: str
    books: int
