from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    name: str
    folder_id: Optional[int] = None
    is_public: bool = False

class FileCreate(FileBase):
    pass

class FileUpdate(BaseModel):
    name: Optional[str] = None
    folder_id: Optional[int] = None
    is_public: Optional[bool] = None

class FileOut(BaseModel):
    id: int
    name: str
    path: str
    folder_id: Optional[int]
    is_public: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        orm_mode = True
