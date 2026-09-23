from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=schemas.MediaTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_media_task(
    task_in: schemas.MediaTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_task(db=db, task_in=task_in)


@router.get("/{task_id}", response_model=schemas.MediaTaskResponse)
async def get_media_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    db_task = await crud.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return db_task