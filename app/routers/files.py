from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.file_service import (
    delete_file_by_id,
    get_file_by_id,
    save_file
)

router = APIRouter()

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(default=None),  
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if folder_id in (None, "", "null", "None"):
        folder_id_int = None
    else:
        try:
            folder_id_int = int(folder_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="folder_id must be an integer")

    file_path = save_file(file, file.filename, user.id, db, folder_id_int)
    if not file_path:
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

    if folder_id_int:
        return RedirectResponse(url=f"/?folder_id={folder_id_int}&msg=Файл загружен", status_code=303)
    return RedirectResponse(url="/?msg=Файл загружен", status_code=303)

@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    file = get_file_by_id(file_id, db)
    if not file:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path=file.path, filename=file.name, media_type="application/octet-stream")

@router.post("/delete/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    delete_file_by_id(file_id, db)
    return RedirectResponse(url="/?msg=Файл удален", status_code=303)
