from pydantic import BaseModel

class TextCreate(BaseModel):
    text: str
    label: int

class TextRead(BaseModel):
    id: int
    text: str
    label: int

    class Config:
        orm_mode = True