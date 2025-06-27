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
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score, accuracy_score, confusion_matrix

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
    raw_df = df.fillna("")
    df = df[['full_text', 'label']]

    # hanya gunakan data yang positif atau negatif. netral diabaikan
    df = df[df['label'] != 2]

    os.remove(temp_path)  # hapus data temp file excel upload

    # 2 | aplikasi text preprocessing (data cleaning, stopwords removal, stemming)
    df = await text_preprocessing()

    # hapus data yang duplikat dan null
    df = df.dropna(subset='stemming')  # hapus data null
    df = df.drop_duplicates(subset='stemming')  # hapus data duplikat
    df = df[df['stemming'] != '']  # hapus string kosong

    # print(f'[DEBUG]: jumlah data: {len(df)}')
    # print(df.head(10))

    # 3 | Vectorization & Classification

    # split data
    X = df['stemming']
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        # sama dengan konfigurasi app di model selection
        X, y, test_size=0.33, random_state=42)

    # 3.a | Naive Bayes
    nb_results = nb_model.predict(X_test)
    # print('[DEBUG]: Hasil Klasifikasi NB')
    # print(nb_results)
    # 3.b | Support Vector Machine
    svm_results = svm_model.predict(X_test)
    # print('[DEBUG]: Hasil Klasifikasi SVM')
    # print(svm_results)

    # 4 | Model Evaluation
    # print("[DEBUG]: Evaluasi Naive Bayes: ")
    # print(accuracy_score(y_test, nb_results))
    # print(classification_report(y_test, nb_results, zero_division=0))
    # print(confusion_matrix(y_test, nb_results))
    # print("[DEBUG]: Evaluasi Support Vector Machine: ")
    # print(accuracy_score(y_test, svm_results))
    # print(classification_report(y_test, svm_results, zero_division=0))
    # print(confusion_matrix(y_test, svm_results))

    # format nilai evaluasi agar dapat ditampilkan di front-end
    nb_eval = {
        "accuracy": accuracy_score(y_test, nb_results),
        "classification_report": classification_report(y_test, nb_results, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, nb_results).tolist(),
    }
    svm_eval = {
        "accuracy": accuracy_score(y_test, svm_results),
        "classification_report": classification_report(y_test, svm_results, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, svm_results).tolist(),
    }

    # 4.a | konversi data df ke JSON
    data = df.to_dict(orient="records")
    raw_data = raw_df.to_dict(orient="records")

    # 4.b | gabungkan data klasifikasi dengan data testing
    df_csf = pd.DataFrame({
        'text': X_test,
        'true_label': y_test,
        'pred_nb': nb_results,
        'pred_svm': svm_results,
    })

    # 5 | Return hasil

    return {
        # "nb_classification": nb_results.tolist(),  # hasil klasifikasi NB
        # "svm_classification": svm_results.tolist(),  # hasil klasifikasi SVM
        "classification": df_csf.to_dict(orient="records"),
        "nb_evaluation": nb_eval,  # evaluasi pengklasifikasian NB
        "svm_evaluation": svm_eval,  # evaluasi pengklasifikasian SVM
        "data": data,
        "raw_data": raw_data,

    }
