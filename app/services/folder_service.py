import os
import shutil
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.config import STORAGE_NODES, UPLOAD_DIR
from app.models import Folder
from app.models.file import File
from app.schemas.folder import FolderCreate, FolderUpdate

def get_folder(db: Session, folder_id: int) -> Optional[Folder]:
    return db.query(Folder).filter(Folder.id == folder_id).first()

def get_folders(db: Session, owner_id: int) -> List[Folder]:
    return db.query(Folder).filter(Folder.owner_id == owner_id).all()

def get_folder_disk_path(db: Session, owner_id: int, folder_id: int, node: str) -> str:
    path_parts = []
    current_folder_id = folder_id

    while current_folder_id:
        folder = db.query(Folder).filter(Folder.id == current_folder_id).first()
        if not folder:
            break
        path_parts.append(f"folder_{folder.id}")
        current_folder_id = folder.parent_id

    path_parts.reverse()

    base_path = os.path.join(UPLOAD_DIR, node, f"user_{owner_id}")
    full_path = os.path.join(base_path, *path_parts)
    return full_path

def create_folder(db: Session, folder: FolderCreate, owner_id: int) -> Folder:
    parent_id = folder.parent_id if folder.parent_id and folder.parent_id != 0 else None

    existing_folder = db.query(Folder).filter_by(
        name=folder.name,
        parent_id=parent_id,
        owner_id=owner_id
    ).first()
    if existing_folder:
        raise HTTPException(status_code=400, detail="Папка с таким именем уже существует в этом каталоге.")

    db_folder = Folder(
        name=folder.name,
        parent_id=parent_id,
        owner_id=owner_id
    )
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    for node in STORAGE_NODES:
        folder_path = get_folder_disk_path(db, owner_id, db_folder.id, node)
        os.makedirs(folder_path, exist_ok=True)

    return db_folder


def update_folder(db: Session, folder_id: int, folder_update: FolderUpdate) -> Optional[Folder]:
    db_folder = get_folder(db, folder_id)
    if not db_folder:
        return None

    if folder_update.name is not None:
        db_folder.name = folder_update.name
    if folder_update.parent_id is not None:
        db_folder.parent_id = folder_update.parent_id

    db.commit()
    db.refresh(db_folder)
    return db_folder

def delete_folder(db: Session, folder_id: int, owner_id: int) -> bool:
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == owner_id).first()
    if not folder:
        return False

    def delete_folder_recursive(fold: Folder):
        files = db.query(File).filter(File.folder_id == fold.id).all()
        for file in files:
            if os.path.exists(file.path):
                os.remove(file.path)
            db.delete(file)

        subfolders = db.query(Folder).filter(Folder.parent_id == fold.id).all()
        for subf in subfolders:
            delete_folder_recursive(subf)

        for node in STORAGE_NODES:
            try:
                full_path = get_folder_disk_path(db, owner_id, fold.id, node)
                if os.path.exists(full_path):
                    shutil.rmtree(full_path)
            except Exception as e:
                print(f"Ошибка при удалении папки на узле '{node}': {e}")

        db.delete(fold)

    delete_folder_recursive(folder)
    db.commit()
    return True
