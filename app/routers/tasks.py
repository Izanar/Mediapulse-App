# app/routers/tasks.py
import os
import shutil
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import crud, schemas, models

router = APIRouter(prefix="/tasks", tags=["Tasks"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=List[schemas.MediaTaskResponse])
async def get_media_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await crud.get_user_tasks(db=db, user_id=current_user.id)


@router.post("/upload", response_model=schemas.MediaTaskResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Приём файла, сохранение на диск и создание задачи."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не выбран")

    # Имя файла с префиксом UUID пользователя для исключения коллизий
    saved_filename = f"{current_user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")

    task = await crud.create_media_task_with_file(
        db=db,
        user_id=current_user.id,
        original_filename=file.filename,
        file_path=file_path
    )
    return task