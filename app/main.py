from fastapi import FastAPI
from app.routers import users
from app.routers import text
from app.database import Base, engine
import pyodbc

# print(pyodbc.drivers())

# buat tabel
Base.metadata.create_all(bind=engine)

app = FastAPI()

# registrasi router
app.include_router(users.router)
app.include_router(text.router)

@app.get("/")
def read_root():
    return {"message: ", "Hello from FastAPI"}