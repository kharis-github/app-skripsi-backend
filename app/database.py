# program untuk menghubungkan sistem ke database SQL Server

from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
print("[DEBUG] env_path = ", env_path)
load_dotenv(dotenv_path=env_path, override=True)

print("[DEBUG] DB_USER = ", f"{os.getenv('DB_USER')}")
print("[DEBUG] DB_PASSWORD = ", f"{os.getenv('DB_PASSWORD')}")
print("[DEBUG] DB_SERVER = ", f"{os.getenv('DB_SERVER')}")
print("[DEBUG] DB_DATABASE = ", f"{os.getenv('DB_DATABASE')}")

# Format URL koneksi
DB_URL = (
    f"mssql+pyodbc://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_SERVER')},{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server"
)

print("[DEBUG] DB_URL = ", DB_URL)

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
