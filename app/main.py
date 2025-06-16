from fastapi import FastAPI
from app.routers import users
from app.routers import text
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
import pyodbc

# print(pyodbc.drivers())

# origins yang terverifikasi
origins = [
    "http://localhost:5173",
]

# buat tabel
Base.metadata.create_all(bind=engine)

app = FastAPI()

# MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # TODO: spesifikasi header-header HTTP yang lebih rinci (mis. ['GET', 'POST', 'PUT', 'DELETE'])
    allow_headers=["*"],
)

# registrasi router
app.include_router(users.router)
app.include_router(text.router)


@app.get("/")
def read_root():
    return {"message: ", "Hello from FastAPI"}
