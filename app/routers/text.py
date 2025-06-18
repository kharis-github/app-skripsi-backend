from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.text import LabeledText
from app.schemas.text import TextCreate, TextRead
from app.crud.text import insert_rows_from_dataframe
import pandas as pd
import pyodbc
import os

router = APIRouter(prefix="/text", tags=["Text"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TextRead)
def create_text(data: TextCreate, db: Session = Depends(get_db)):
    new_data = LabeledText(**data.dict())
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data


@router.get("/", response_model=list[TextRead])
def list_texts(db: Session = Depends(get_db)):
    text = db.query(LabeledText).all()
    print(f"[DEBUG] Data text = {text}")
    return text

# TODO: upload data mentah


@router.post("/upload")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # buka file yang diupload
    contents = await file.read()
    temp_path = "temp.xlsx"
    with open(temp_path, "wb") as f:
        f.write(contents)

    # konversi file menjadi pandas dataframe
    df = pd.read_excel(temp_path)

    # laksanakan proses insert CRUD
    insert_rows_from_dataframe(db, df)

    # hapus file temporer usai proses insert
    os.remove(temp_path)

    # send json confirm sukses proses
    return {"status": "success"}
