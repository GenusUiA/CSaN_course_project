import os
from typing import List, Optional
import uuid
from fastapi import HTTPException, UploadFile
from app.schemas.file_version import FileVersionCreate
from app.services.file_version_service import create_file_version, get_versions_by_file_id
from app.services.folder_service import get_folder_disk_path
from app.services.storage_node import choose_storage_node
from app.config import UPLOAD_DIR
from sqlalchemy.orm import Session
from app.models import File

def save_file(
    file: UploadFile,
    filename: str,
    user_id: int,
    db: Session,
    folder_id: Optional[int] = None
) -> str:
    node = choose_storage_node()
    
    if folder_id:
        user_dir = get_folder_disk_path(db, user_id, folder_id, node)
    else:
        user_dir = os.path.join(UPLOAD_DIR, node, f"user_{user_id}")

    os.makedirs(user_dir, exist_ok=True)

    existing_file = db.query(File).filter_by(
        owner_id=user_id,
        folder_id=folder_id,
        name=filename
    ).first()

    unique_filename = f"{uuid.uuid4()}_{filename}"
    new_file_path = os.path.join(user_dir, unique_filename)

    with open(new_file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)

    if existing_file:
        if os.path.exists(existing_file.path):
            existing_versions = get_versions_by_file_id(existing_file.id, db)
            new_version_number = (existing_versions[0].version_number + 1) if existing_versions else 1

            create_file_version(
                existing_file.id,
                FileVersionCreate(
                    version_number=new_version_number,
                    path=existing_file.path
                ),
                db
            )

        existing_file.path = new_file_path
        db.commit()
        db.refresh(existing_file)
        return new_file_path

    db_file = File(
        name=filename,
        path=new_file_path,
        owner_id=user_id,
        folder_id=folder_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    create_file_version(
        db_file.id,
        FileVersionCreate(version_number=1, path=new_file_path),
        db
    )
    return new_file_path

def get_file_by_id(file_id: int, db: Session) -> File:
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Файл не найден в базе данных")

    if not os.path.exists(file.path):
        raise HTTPException(status_code=410, detail="Файл отсутствует на сервере (возможно удалён)")

    return file

def delete_file_by_id(file_id: int, db: Session) -> None:
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    versions = get_versions_by_file_id(file_id, db)
    for version in versions:
        if os.path.exists(version.path):
            try:
                os.remove(version.path)
            except Exception as e:
                print(f"Ошибка при удалении версии файла {version.path}: {e}")
        else:
            print(f"Версия файла {version.path} не найдена на диске")

    if os.path.exists(file.path):
        try:
            os.remove(file.path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении файла с диска: {e}")
    else:
        print(f"Файл {file.path} не найден на диске, но запись удаляется из БД")

    db.delete(file)
    db.commit()


def get_files_by_user(user_id: int, db: Session) -> List[File]:
    all_files = db.query(File).filter(File.owner_id == user_id).all()

    existing_files = [f for f in all_files if os.path.exists(f.path)]

    return existing_files

def get_file_by_id(file_id: int, db: Session) -> File:
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return file