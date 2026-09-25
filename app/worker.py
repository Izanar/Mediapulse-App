import io
import os
import uuid
from PIL import Image, ImageOps
from celery import Celery
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import MediaTask, TaskStatus
from app.storage import download_file_from_s3, upload_file_to_s3

# Настройка Celery
celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# Безопасное получение DATABASE_URL с дефолтным значением
db_url = getattr(settings, "DATABASE_URL", None) or os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mediapulse"
)

# Преобразуем asyncpg в стандартный драйвер postgresql для синхронного SQLAlchemy в Celery
SYNC_DATABASE_URL = db_url.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(name="process_media_task")
def process_media_task(task_id_str: str, storage_key: str, processed_key: str):
    """
    Фоновая задача Celery:
    1. Скачивает файл из S3.
    2. Инвертирует цвета изображения в RAM.
    3. Сохраняет обработанный файл обратно в S3.
    4. Обновляет статус записи в БД.
    """
    task_id = uuid.UUID(task_id_str)
    db = SessionLocal()

    try:
        task = db.execute(select(MediaTask).where(MediaTask.id == task_id)).scalars().first()
        if not task:
            return f"Task {task_id_str} not found"

        task.status = TaskStatus.PROCESSING
        db.commit()

        # 1. Скачивание исходного изображения из S3
        image_bytes = download_file_from_s3(settings.S3_BUCKET_NAME, storage_key)

        # 2. Обработка изображения с использованием Pillow
        image = Image.open(io.BytesIO(image_bytes))

        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb_image = Image.merge("RGB", (r, g, b))
            inverted_image = ImageOps.invert(rgb_image)
            r, g, b = inverted_image.split()
            inverted_image = Image.merge("RGBA", (r, g, b, a))
        else:
            rgb_image = image.convert("RGB")
            inverted_image = ImageOps.invert(rgb_image)

        output_buffer = io.BytesIO()
        inverted_image.save(output_buffer, format="PNG")
        processed_bytes = output_buffer.getvalue()

        # 3. Выгрузка обработанного изображения обратно в S3
        upload_file_to_s3(
            file_bytes=processed_bytes,
            bucket_name=settings.S3_BUCKET_NAME,
            object_name=processed_key,
        )

        # 4. Обновление статуса, ключа и путей в БД
        task.processed_path = f"/api/v1/tasks/file/{task_id}/processed"  # <--- Обязательно с /api/v1!
        task.processed_key = processed_key
        task.status = TaskStatus.COMPLETED
        db.commit()

        return f"Task {task_id_str} completed successfully"

    except Exception as e:
        db.rollback()
        task = db.execute(select(MediaTask).where(MediaTask.id == task_id)).scalars().first()
        if task:
            task.status = TaskStatus.FAILED
            db.commit()
        raise e
    finally:
        db.close()