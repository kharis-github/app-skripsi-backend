# ORM untuk dataset text scraping dari twitter
from sqlalchemy import Column, Integer, Text, String, DateTime
from app.database import Base
from datetime import datetime

# model for text object


class LabeledText(Base):
    __tablename__ = "text"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    label = Column(Integer, nullable=False)

# model for raw twitter data


class RawText(Base):
    __tablename__ = "rawtext"

    id = Column(Integer, nullable=False, primary_key=True)
    conversation_id_str = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    favorite_count = Column(Integer)
    full_text = Column(Text)
    id_str = Column(String(255))
    image_url = Column(String(255))
    in_reply_to_screen_name = Column(String(100))
    lang = Column(String(4))
    location = Column(String(100))
    quote_count = Column(Integer)
    reply_count = Column(Integer)
    retweet_count = Column(Integer)
    tweet_url = Column(String(100))
    user_id_str = Column(String(255))
    username = Column(String(100))
