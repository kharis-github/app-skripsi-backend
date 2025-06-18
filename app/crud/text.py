from sqlalchemy.orm import Session
from app.models.text import RawText
import pandas as pd

# insert raw text


def insert_rows_from_dataframe(db: Session, df: pd.DataFrame):
    for _, row in df.iterrows():
        # input data ke tabel RawText
        item = RawText(
            conversation_id_str=str(row[0]),
            created_at=pd.to_datetime(row[1]),
            favorite_count=int(row[2]),
            full_text=str(row[3]),
            id_str=str(row[4]),
            image_url=str(row[5]),
            in_reply_to_screen_name=str(row[6]),
            lang=str(row[7]),
            location=str(row[8]),
            quote_count=int(row[9]),
            reply_count=int(row[10]),
            retweet_count=int(row[11]),
            tweet_url=str(row[12]),
            user_id_str=str(row[13]),
            username=str(row[14])
        )
        db.add(item)
    db.commit()
