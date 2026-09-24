# app/crud.py
from uuid import UUID
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, MediaTask  # проверь название модели задач (Task или MediaTask)
from app.schemas import UserCreate, MediaTaskCreate
from app.auth import get_password_hash


# --- USERS ---

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=getattr(user_in, "username", user_in.email),
        email=getattr(user_in, "email", None),
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# --- TASKS ---

async def get_user_tasks(db: AsyncSession, user_id: UUID) -> Sequence[MediaTask]:
    """Получить список всех задач конкретного пользователя."""
    result = await db.execute(
        select(MediaTask).where(MediaTask.user_id == user_id)
    )
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: UUID) -> MediaTask | None:
    """Получить задачу по её ID."""
    result = await db.execute(
        select(MediaTask).where(MediaTask.id == task_id)
    )
    return result.scalars().first()


async def create_task(db: AsyncSession, task_in: MediaTaskCreate, user_id: UUID) -> MediaTask:
    """Создать новую задачу."""
    db_task = MediaTask(
        **task_in.model_dump(),
        user_id=user_id
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task