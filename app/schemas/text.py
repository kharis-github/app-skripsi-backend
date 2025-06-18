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

# raw text dasar


class RawTextBase(BaseModel):
    conversation_id_str: str

# read text


class RawTextRead(RawTextBase):
    pass
