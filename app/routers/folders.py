from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.services.auth_service import get_current_user
from app.services.folder_service import (
    get_folder,
    get_folders,
    create_folder,
    update_folder,
    delete_folder,
)

router = APIRouter(
    prefix="/folders",
    tags=["Folders"],
)

@router.get("/", response_model=List[FolderRead])
def read_folders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    folders = get_folders(db, owner_id=current_user.id)
    return folders

@router.get("/{folder_id}", response_model=FolderRead)
def read_folder(folder_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    folder = get_folder(db, folder_id)
    if not folder or folder.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.post("/", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
def create_new_folder(
    name: str = Form(...),
    parent_id: Optional[str] = Form(None), 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if parent_id == "" or parent_id is None:
        parent_id_int = None
    else:
        try:
            parent_id_int = int(parent_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="parent_id must be an integer")
    
    folder_data = FolderCreate(name=name, parent_id=parent_id_int)
    create_folder(db, folder_data, owner_id=current_user.id)

    if parent_id_int in (None, 0):
        redirect_url = "/"
    else:
        redirect_url = f"/?folder_id={parent_id_int}"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@router.put("/{folder_id}", response_model=FolderRead)
def update_existing_folder(folder_id: int, folder_update: FolderUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    folder = get_folder(db, folder_id)
    if not folder or folder.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    updated_folder = update_folder(db, folder_id, folder_update)
    return updated_folder

@router.post("/delete/{folder_id}", response_class=RedirectResponse)
def delete_folder_and_redirect(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    folder = get_folder(db, folder_id)
    if not folder or folder.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Folder not found")

    parent_id = folder.parent_id 
    
    delete_folder(db, folder_id, current_user.id)

    if parent_id:
        redirect_url = f"/?folders/{parent_id}" 
    else:
        redirect_url = "/"

    return RedirectResponse(url=redirect_url, status_code=303)
