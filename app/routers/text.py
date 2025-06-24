from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.text import LabeledText, RawText
from app.schemas.text import TextCreate, TextRead
from app.crud.text import insert_rows_from_dataframe
from pathlib import Path
import pandas as pd
import pyodbc
import os
import joblib
from app.classification.text import text_cleaning, normalisasi, stopwords_removal, tokenize, stemming, get_slang_dict, text_preprocessing

router = APIRouter(prefix="/text", tags=["Text"])

# konfigurasi direktori
current_dir = Path(__file__).resolve().parent
nb_model_path = current_dir.parent / "classification" / "nb_model.joblib"
svm_model_path = current_dir.parent / "classification" / "svm_model.joblib"

# load model NB dan SVM
nb_model = joblib.load(nb_model_path)  # naive bayes
svm_model = joblib.load(svm_model_path)  # support vector machine


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
    # print(f"[DEBUG] Data text = {text}")
    return text

# upload dataset penelitian dari excel untuk disimpan di database


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

# get raw data


@router.get("/get")
def list_texts(db: Session = Depends(get_db)):
    text = db.query(RawText).all()
    # print(f"[DEBUG] Data text = {text}")
    return text

# proses dan klasifikasi data penelitian untuk simulasi proses


@router.post("/classify")
async def predict_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1 | buka file excel upload, dan simpan di dalam pandas dataframe
    contents = await file.read()
    temp_path = "temp.xlsx"
    with open(temp_path, "wb") as f:
        f.write(contents)

    df = pd.read_excel(temp_path)
    df = df[['full_text', 'label']]

    # 2 | aplikasi text preprocessing (data cleaning, stopwords removal, stemming)
    df = await text_preprocessing(df.head(10))  # DEBUG: sample 10 data

    # hapus data yang duplikat dan null
    df = df.dropna(subset='stemming')  # hapus data null
    df = df.drop_duplicates(subset='stemming')  # hapus data duplikat
    df = df[df['stemming'] != '']  # hapus string kosong

    # print(f'[DEBUG]: jumlah data: {len(df)}')
    # print(df.head(10))

    # 3 | Vectorization & Classification
    # 3.a | Naive Bayes
    nb_results = nb_model.predict(df['stemming'])
    # print('[DEBUG]: Hasil Klasifikasi NB')
    # print(nb_results)
    # 3.b | Support Vector Machine
    svm_results = svm_model.predict(df['stemming'])
    # print('[DEBUG]: Hasil Klasifikasi SVM')
    # print(svm_results)

    # 4 | Model Evaluation

    os.remove(temp_path)  # hapus data temp file excel upload

    # 4.a | konversi data df ke JSON
    data = df.to_dict(orient="records")

    return {
        "nb_classification": nb_results.tolist(),  # hasil klasifikasi NB
        "svm_classification": svm_results.tolist(),  # hasil klasifikasi SVM
        "data": data,

    }
