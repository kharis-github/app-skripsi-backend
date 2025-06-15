from fastapi import FastAPI
from app.routers import users
from app.database import Base, engine

# buat tabel
Base.metadata.create_all(bind=engine)

app = FastAPI()

# registrasi router
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message: ", "Hello from FastAPI"}