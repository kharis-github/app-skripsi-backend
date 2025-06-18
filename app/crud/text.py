from sqlalchemy.orm import Session
from app.models.text import RawText
import pandas as pd

# insert raw text


def insert_rows_from_dataframe(db: Session, df: pd.DataFrame):
    for _, row in df.iterrows():
        # input data ke tabel RawText
        item = RawText(
            conversation_id_str=None if pd.isna(row[0]) else str(row[0]),
            created_at=None if pd.isna(row[1]) else pd.to_datetime(row[1]),
            favorite_count=None if pd.isna(row[2]) else int(row[2]),
            full_text=None if pd.isna(row[3]) else str(row[3]),
            id_str=None if pd.isna(row[4]) else str(row[4]),
            image_url=None if pd.isna(row[5]) else str(row[5]),
            in_reply_to_screen_name=None if pd.isna(row[6]) else str(row[6]),
            lang=None if pd.isna(row[7]) else str(row[7]),
            location=None if pd.isna(row[8]) else str(row[8]),
            quote_count=None if pd.isna(row[9]) else int(row[9]),
            reply_count=None if pd.isna(row[10]) else int(row[10]),
            retweet_count=None if pd.isna(row[11]) else int(row[11]),
            tweet_url=None if pd.isna(row[12]) else str(row[12]),
            user_id_str=None if pd.isna(row[13]) else str(row[13]),
            username=None if pd.isna(row[14]) else str(row[14])
        )
        db.add(item)
    db.commit()
