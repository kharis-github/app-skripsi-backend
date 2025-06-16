from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.text import Text
from app.schemas.text import TextCreate, TextRead

router = APIRouter(prefix="/text", tags=["Text"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TextRead)
def create_text(data: TextCreate, db: Session = Depends(get_db)):
    new_data = Text(**data.dict())
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

@router.get("/", response_model=list[TextRead])
def list_texts(db: Session = Depends(get_db)):
    text =  db.query(Text).all()
    print(f"[DEBUG] Data text = {text}")
    return text