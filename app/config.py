import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL не установлена в .env! Использую sqlite по умолчанию.")
    DATABASE_URL = "sqlite:///./test.db"

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_files")
if not os.path.exists(UPLOAD_DIR):
    logger.info(f"Создаю директорию для загрузки файлов: {UPLOAD_DIR}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

storage_nodes_env = os.getenv("STORAGE_NODES", "node_1,node_2")
STORAGE_NODES = [node.strip() for node in storage_nodes_env.split(",") if node.strip()]

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key")
    ALGORITHM = "HS256"

settings = Settings()

if not os.path.exists(UPLOAD_DIR):
    logger.info(f"Создаю директорию для загрузки файлов: {UPLOAD_DIR}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

for node in STORAGE_NODES:
    node_path = os.path.join(UPLOAD_DIR, node)
    if not os.path.exists(node_path):
        logger.info(f"Создаю узел хранения: {node_path}")
        os.makedirs(node_path, exist_ok=True)

# logger.info(f"Используем базу данных: {DATABASE_URL}")
# logger.info(f"Директория для файлов: {UPLOAD_DIR}")
# logger.info(f"Доступные узлы хранения: {STORAGE_NODES}")
