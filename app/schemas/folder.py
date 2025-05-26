from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

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

class FolderBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class FolderCreate(FolderBase):
    pass

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None

class FolderRead(FolderBase):
    id: int
    owner_id: int
    subfolders: List["FolderRead"] = []
    files: List[FileOut] = []

    class Config:
        orm_mode = True

FolderRead.update_forward_refs()
