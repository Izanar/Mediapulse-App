import io
import os
import asyncio
from uuid import UUID
from celery import Celery
from PIL import Image, ImageOps
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import TaskStatus
from app import crud
from app.storage import download_file_from_s3, upload_file_to_s3 # или твоя логика работы с файлами

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    broker_connection_retry_on_startup=True
)

@celery_app.task(bind=True, name="process_image_task")
def process_image_task(self, task_id: str):
    async def async_process():
        async with AsyncSessionLocal() as db:
            # 1. Получаем задачу через асинхронный CRUD
            task_uuid = UUID(task_id) if isinstance(task_id, str) else task_id
            task = await crud.get_task_by_id(db, task_uuid)
            if not task:
                return
            
            # Обновляем статус на PROCESSING (если есть соответствующий метод или через прямое изменение)
            task.status = TaskStatus.PROCESSING
            await db.commit()

            try:
                # 2. Скачиваем файл из S3, используя точный путь из базы данных (storage_path)
                # Если у вас файлы хранятся строго в S3:
                file_bytes = download_file_from_s3(settings.S3_BUCKET_NAME, task.storage_path)

                # 3. Обработка изображения (Pillow)
                image = Image.open(io.BytesIO(file_bytes))
                if image.mode in ("RGBA", "LA"):
                    image = image.convert("RGB")
                
                processed_image = ImageOps.invert(image)

                output_buffer = io.BytesIO()
                processed_image.save(output_buffer, format="JPEG")
                processed_bytes = output_buffer.getvalue()

                # 4. Загрузка результата
                processed_path = f"uploads/processed_{task_id}.jpg"
                # Если сохраняешь локально или в S3:
                upload_file_to_s3(processed_bytes, "media-processed", processed_path)

                # 5. Обновляем статус на COMPLETED
                task.status = TaskStatus.COMPLETED
                task.processed_path = processed_path
                await db.commit()

            except Exception as e:
                await db.rollback()
                task.status = TaskStatus.FAILED
                await db.commit()
                raise e

    # Запускаем асинхронный код внутри синхронной задачи Celery
    asyncio.run(async_process())