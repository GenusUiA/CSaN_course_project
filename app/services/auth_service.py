import os
from fastapi import Depends, Request
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from app.models.folder import Folder
from app.models.user import User
from sqlalchemy.orm import Session
from app.config import STORAGE_NODES, UPLOAD_DIR, settings  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(data:dict):
    return create_token(data, timedelta(minutes=15))

def create_refresh_token(data:dict):
    return create_token(data, timedelta(days=7))

def create_user(db: Session, email: str, password: str):
    hashed_pw = hash_password(password)
    user = User(email=email, password_hash=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    user_folder_name = f"user_{user.id}"

    for node in STORAGE_NODES:
        node_user_path = os.path.join(UPLOAD_DIR, node, user_folder_name)
        os.makedirs(node_user_path, exist_ok=True)

    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    
    if not token:
        return None
    try:
        scheme, _, param = token.partition(" ")
        if scheme.lower() != "bearer":
            return None
        payload = jwt.decode(param, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.email == email).first()
    return user