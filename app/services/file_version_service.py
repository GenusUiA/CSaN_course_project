from sqlalchemy.orm import Session
from app.models.file_version import FileVersion
from app.models.file import File
from app.schemas.file_version import FileVersionCreate
from fastapi import HTTPException

def create_file_version(file_id: int, version_data: FileVersionCreate, db: Session) -> FileVersion:
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Такого файла не существует")

    new_version = FileVersion(
        file_id=file_id,
        version_number=version_data.version_number,
        path=version_data.path
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version

def get_versions_by_file_id(file_id: int, db: Session):
    return db.query(FileVersion).filter(FileVersion.file_id == file_id).order_by(FileVersion.version_number.desc()).all()

def get_file_version(version_id: int, db: Session) -> FileVersion:
    version = db.query(FileVersion).filter(FileVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Версия не найдена")
    return version
