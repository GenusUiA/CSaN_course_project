from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    files = relationship(
        "File",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    folders = relationship(
        "Folder",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
