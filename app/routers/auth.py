from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services import auth_service
from jose import JWTError, jwt
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="design/templates")

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Пользователь уже существует"
        })

    user = auth_service.create_user(db, email, password)
    access_token = auth_service.create_access_token({"sub": user.email})
    refresh_token = auth_service.create_refresh_token({"sub": user.email})

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True)
    response.set_cookie("refresh_token", f"Bearer {refresh_token}", httponly=True, secure = True, samesite="Strict")
    return response

@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = auth_service.authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    access_token = auth_service.create_access_token({"sub": user.email})
    refresh_token = auth_service.create_refresh_token({"sub": user.email})

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True)
    response.set_cookie("refresh_token", f"Bearer {refresh_token}", httponly=True, secure = True, samesite="Strict" )
    return response

@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@router.post("/refresh", response_class=JSONResponse)
async def refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    scheme, _, param = token.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token scheme")

    try:
        payload = jwt.decode(param, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = auth_service.create_access_token({"sub": email})
    
    response = JSONResponse({"message": "Token refreshed"})
    response.set_cookie(
        "access_token", f"Bearer {new_access_token}",
        httponly=True,
        secure=True,
        samesite="Strict"
    )
    return response
