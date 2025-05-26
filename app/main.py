from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.folder import Folder
from app.routers import auth, folders, users, files, file_version
import app.models
from app.services.auth_service import get_current_user
from app.models.file import File 
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
# Подключение статики и шаблонов
app.mount("/static", StaticFiles(directory="design/static"), name="static")
templates = Jinja2Templates(directory="design/templates")

# Подключение маршрутов
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="", tags=["Users"])
app.include_router(files.router, prefix="/file", tags = ["Files"])
app.include_router(folders.router)
app.include_router(file_version.router, prefix="/versions", tags=["File Versions"])
@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    folder_id: int = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    current_folder = None
    subfolders = []
    files = []
    
    if not user:
        return templates.TemplateResponse("home.html", {"request": request, "user": None})

    if folder_id:
        current_folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == user.id).first()
        if current_folder:
            subfolders = current_folder.subfolders
            files = current_folder.files
    else:
        subfolders = db.query(Folder).filter(Folder.owner_id == user.id, Folder.parent_id == None).all()
        files = db.query(File).filter(File.owner_id == user.id, File.folder_id == None).all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user,
        "current_folder": current_folder,
        "folders": subfolders,
        "files": files
    })