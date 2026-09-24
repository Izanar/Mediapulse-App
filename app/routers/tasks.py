from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user  # Импортируем текущего пользователя
from app import crud, schemas, models

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# 1. Получение списка задач (НОВЫЙ ЭНДПОИНТ)
@router.get("/", response_model=List[schemas.MediaTaskResponse])
async def get_media_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Если задачи привязаны к пользователю:
    return await crud.get_user_tasks(db=db, user_id=current_user.id)
    # Или если получаешь вообще все задачи без привязки к user_id:
    # return await crud.get_all_tasks(db=db)


# 2. Создание задачи
@router.post("/", response_model=schemas.MediaTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_media_task(
    task_in: schemas.MediaTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await crud.create_task(db=db, task_in=task_in, user_id=current_user.id)


# 3. Получение одной задачи по ID
@router.get("/{task_id}", response_model=schemas.MediaTaskResponse)
async def get_media_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_task = await crud.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return db_task