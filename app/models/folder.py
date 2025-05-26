from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    parent = relationship("Folder", remote_side=[id], backref="subfolders", passive_deletes=True)
    owner = relationship("User", back_populates="folders")
    files = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
