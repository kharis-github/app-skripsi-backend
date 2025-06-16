# ORM untuk dataset text scraping dari twitter
from sqlalchemy import Column, Integer, Text
from app.database import Base

# model for text object


class Text(Base):
    __tablename__ = "text"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    label = Column(Integer, nullable=False)
