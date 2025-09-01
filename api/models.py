from sqlalchemy import Column, Integer, String, Float
from api.database import Base


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    upc = Column(String, index=True, nullable=True)
    title = Column(String, index=True)
    price = Column(Float, index=True)
    rating = Column(Integer, index=True)
    availability = Column(Integer, default=0)
    category = Column(String, index=True)
    image_url = Column(String, nullable=True)
    product_page_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
