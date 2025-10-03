from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from logic import process_files_and_query
import tempfile
import os
import logging

# Настройка логирования
import sys
from datetime import datetime

# Создаем папку для логов если её нет
os.makedirs("logs", exist_ok=True)

# Настраиваем логирование в файл и консоль
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку с фронтендом
frontend_path = "./frontend"
if os.path.exists(frontend_path):
    # Монтируем статические файлы фронтенда
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"Фронтенд смонтирован по пути: {frontend_path}")
    
    # Добавляем обработчик для корневого пути фронтенда
    @app.get("/frontend/")
    async def frontend_index():
        """Возвращаем index.html для корневого пути фронтенда"""
        from fastapi.responses import FileResponse
        index_path = os.path.join(frontend_path, "index.html")
        logger.info(f"Запрос на /frontend/, ищем файл: {index_path}")
        logger.info(f"Файл существует: {os.path.exists(index_path)}")
        if os.path.exists(index_path):
            logger.info(f"Возвращаем index.html из {index_path}")
            return FileResponse(index_path)
        else:
            logger.error(f"index.html не найден в {index_path}")
            return {"error": "index.html не найден"}
else:
    logger.error(f"Папка фронтенда не найдена: {frontend_path}")
    logger.info(f"Текущая рабочая директория: {os.getcwd()}")
    logger.info(f"Содержимое директории: {os.listdir('.')}")

# Директория для загрузки файлов (используем системную временную директорию)
UPLOAD_DIR = tempfile.mkdtemp(prefix="upload_")
logger.info(f"Файлы будут загружаться в директорию: {UPLOAD_DIR}")

@app.get("/")
async def root():
    """Перенаправляем на фронтенд"""
    logger.info("Получен запрос на корневой путь, перенаправляем на /frontend/")
    return RedirectResponse(url="/frontend/")

@app.post("/query/")
async def handle_query(prompt: str = Form(...), files: list[UploadFile] = File(default=[])):
    """Принимает промт и файлы, запускает бизнес-логику и стримит ответ."""
    try:
        logger.info(f"Получен запрос с промтом: '{prompt[:50]}...' и {len(files)} файл(ами)")

        file_paths = []
        for uploaded_file in files:
            if uploaded_file.filename:
                file_location = os.path.join(UPLOAD_DIR, uploaded_file.filename)
                with open(file_location, "wb+") as file_object:
                    file_object.write(uploaded_file.file.read())
                file_paths.append(file_location)
                logger.info(f"Файл загружен: {file_location}")

        # Получаем ответ от модели
        response_text = process_files_and_query(prompt, file_paths)
        
        # Опционально: очистить временные файлы после завершения
        # for path in file_paths:
        #     try:
        #         os.remove(path)
        #         logger.info(f"Временный файл удален: {path}")
        #     except OSError as e:
        #         logger.error(f"Не удалось удалить временный файл {path}: {e}")

        # Возвращаем обычный ответ
        return {"response": response_text}
    
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        return {"error": f"Ошибка при обработке запроса: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)