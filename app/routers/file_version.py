import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.file import File
from app.services.auth_service import get_current_user
from app.services.file_service import get_file_by_id
from app.services.file_version_service import (
    create_file_version, get_versions_by_file_id, get_file_version
)
from app.schemas.file_version import FileVersionCreate, FileVersionOut

router = APIRouter()

@router.post("/{file_id}", response_model=FileVersionOut)
def add_version(
    file_id: int,
    version_data: FileVersionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return create_file_version(file_id, version_data, db)

@router.get("/{file_id}", response_model=List[FileVersionOut])
def list_versions(
    file_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_versions_by_file_id(file_id, db)

@router.get("/single/{version_id}", response_model=FileVersionOut)
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_file_version(version_id, db)

templates = Jinja2Templates(directory="design/templates")

@router.get("/file/download_version/{version_id}")
def download_version(version_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    version = get_file_version(version_id, db)
    file = db.query(File).filter(File.id == version.file_id).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="Оригинальный файл не найден")
    
    filename, ext = os.path.splitext(file.name)
    
    versioned_filename = f"{filename}_v{version.version_number}{ext}"
    
    return FileResponse(path=version.path, filename=versioned_filename)

@router.get("/file/{file_id}", response_class=HTMLResponse)
def file_detail(file_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    file = get_file_by_id(file_id, db)
    versions = get_versions_by_file_id(file_id, db)

    versions = get_versions_by_file_id(file_id, db)
    current_version = versions[0] if versions else None
    previous_versions = versions[1:] if len(versions) > 1 else []

    return templates.TemplateResponse("file.html", {
        "request": request,
        "file": {
            "id": file.id,
            "name": file.name,
            "current_version": current_version,
            "versions": previous_versions 
        }
    })