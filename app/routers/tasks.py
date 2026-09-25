import mimetypes
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.auth import get_current_user, get_current_user_optional
from app.config import settings
from app.database import get_db
from app.models import MediaTask, TaskStatus, User
from app.storage import (
    delete_file_from_s3,
    download_file_from_s3,
    generate_s3_paths,
    upload_file_to_s3,
)
from app.worker import process_media_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemas.MediaTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_media_task(
    file: UploadFile = File(...),
    is_public: bool = Form(False),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Принимает файл, загружает его в S3 и отправляет задачу в Celery."""
    content = await file.read()
    username = current_user.username if current_user else "anonymous"
    user_filename = file.filename or "file"

    storage_key, processed_key, _ = generate_s3_paths(
        username=username,
        user_filename=user_filename,
        filename=file.filename or "image.png"
    )

    # Загружаем оригинал в S3
    upload_file_to_s3(
        file_bytes=content,
        bucket_name=settings.S3_BUCKET_NAME,
        object_name=storage_key
    )

    task_id = uuid.uuid4()
    
    # Ссылка для фронтенда (прокси через FastAPI)
    # Ссылка для фронтенда с правильным префиксом API
    storage_url = f"/api/v1/tasks/file/{task_id}/original"
    processed_url = f"/api/v1/tasks/file/{task_id}/processed"

    new_task = MediaTask(
        id=task_id,
        original_filename=user_filename,
        storage_path=storage_url,
        processed_path=processed_url,  # Cразу закладываем путь для обработанного файла
        storage_key=storage_key,       # Сохраняем реальный путь в S3
        processed_key=processed_key,   # Сохраняем будущий путь обработанного файла в S3
        is_public=is_public,
        owner_id=current_user.id if current_user else None,
        status=TaskStatus.PENDING,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Запуск Celery-задачи с передачей ключей S3
    process_media_task.delay(str(new_task.id), storage_key, processed_key)

    return new_task


@router.get("/public", response_model=List[schemas.MediaTaskResponse])
async def get_public_gallery(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MediaTask)
        .where(MediaTask.is_public == True)
        .order_by(MediaTask.id.desc())
    )
    return result.scalars().all()


@router.get("/my", response_model=List[schemas.MediaTaskResponse])
async def get_my_gallery(
    filter_type: str = "all",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(MediaTask).where(MediaTask.owner_id == current_user.id)

    if filter_type == "public":
        query = query.where(MediaTask.is_public == True)
    elif filter_type == "private":
        query = query.where(MediaTask.is_public == False)

    query = query.order_by(MediaTask.id.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/file/{task_id}/{file_type}")
async def get_task_file(
    task_id: uuid.UUID,
    file_type: str,  # 'original' или 'processed'
    db: AsyncSession = Depends(get_db),
):
    """Отдает байты файла напрямую из S3 через FastAPI по точному ключу из БД."""
    result = await db.execute(select(MediaTask).where(MediaTask.id == task_id))
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено",
        )

    # Берем чистый S3 ключ напрямую из базы, никаких костыльных replace!
    object_key = task.storage_key if file_type == "original" else task.processed_key
    
    if not object_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ключ файла в S3 отсутствует",
        )

    try:
        file_bytes = download_file_from_s3(settings.S3_BUCKET_NAME, object_key)

        # Автоматическое определение MIME-типа
        media_type, _ = mimetypes.guess_type(object_key)
        media_type = media_type or "image/png"

        return Response(content=file_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ошибка чтения файла из S3: {e}",
        )


@router.get("/{task_id}", response_model=schemas.MediaTaskResponse)
async def get_task_status(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Получает статус конкретной задачи по её ID."""
    result = await db.execute(select(MediaTask).where(MediaTask.id == task_id))
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено",
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MediaTask).where(
            MediaTask.id == task_id, MediaTask.owner_id == current_user.id
        )
    )
    task = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание не найдено или недостаточно прав",
        )

    # Удаляем оригинал и обработанный файл из S3 по точным ключам из БД
    if task.storage_key:
        try:
            delete_file_from_s3(settings.S3_BUCKET_NAME, task.storage_key)
        except Exception:
            pass

    if task.processed_key:
        try:
            delete_file_from_s3(settings.S3_BUCKET_NAME, task.processed_key)
        except Exception:
            pass

    await db.delete(task)
    await db.commit()
    return None