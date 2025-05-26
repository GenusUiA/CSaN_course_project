from pydantic import BaseModel
from datetime import datetime

class FileVersionBase(BaseModel):
    version_number: int
    path: str
    created_at: datetime

    class Config:
        orm_mode = True

class FileVersionCreate(BaseModel):
    version_number: int
    path: str

class FileVersionOut(FileVersionBase):
    id: int
    file_id: int
