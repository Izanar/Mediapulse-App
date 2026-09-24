import os
from uuid import UUID, uuid4
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import crud, schemas, models
from app.worker import process_image_task
from app.storage import upload_file_to_s3  # Импортируем функцию работы с S3

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Больше не нужно создавать UPLOAD_DIR локально, так как файлы идут сразу в S3


@router.get("/", response_model=List[schemas.MediaTaskResponse])
async def get_media_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Получение списка задач текущего пользователя."""
    return await crud.get_user_tasks(db=db, user_id=current_user.id)


@router.post("/upload", response_model=schemas.MediaTaskResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_file(
    file: UploadFile = File(...),
    is_public: bool = Form(False),  # Флаг публичности из формы
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Приём файла, загрузка оригинала в S3, создание задачи в БД со статусом PENDING 
    и постановка задачи в очередь Celery для инверсии цветов.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не выбран")

    # Читаем содержимое файла в оперативную память
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {str(e)}")

    # Формируем уникальный путь/ключ для файла в S3
    file_id = uuid4()
    storage_path = f"uploads/{file_id}_{file.filename}"

    try:
        # 1. Загружаем оригинал в S3 (в бакет media-originals)
        upload_file_to_s3(file_bytes, "media-originals", storage_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла в S3: {str(e)}")

    # 2. Создаем задачу в базе данных через CRUD-функцию
    task = await crud.create_media_task_with_file(
        db=db,
        user_id=current_user.id,
        original_filename=file.filename,
        file_path=storage_path  # Сохраняем путь в S3
    )
    
    # Если нужно сразу сохранить флаг is_public (убедитесь, что поле есть в модели)
    task.is_public = is_public
    await db.commit()
    await db.refresh(task)

    # 3. Передаем задачу в фоновый воркер Celery через .delay()
    process_image_task.delay(str(task.id))

    return task


@router.get("/{task_id}", response_model=schemas.MediaTaskResponse)
async def get_media_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Получение конкретной задачи с проверкой прав доступа (публичная или владелец)."""
    task = await crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Проверка прав: доступна, если она публичная ИЛИ текущий пользователь — владелец
    if not task.is_public and task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Удаление задачи."""
    task = await crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверка прав: удалять может только владелец
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # При желании здесь можно добавить удаление файлов из S3 бакетов (media-originals и media-processed)

    # Удаляем задачу из базы данных через CRUD
    await crud.delete_media_task(db=db, task=task)
    return None