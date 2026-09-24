from uuid import UUID, uuid4
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, MediaTask, TaskStatus
from app.schemas import UserCreate
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
    """Отримати список усіх задач конкретного користувача."""
    result = await db.execute(
        select(MediaTask).where(MediaTask.owner_id == user_id)
    )
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: UUID) -> MediaTask | None:
    """Отримати задачу за її ID."""
    result = await db.execute(
        select(MediaTask).where(MediaTask.id == task_id)
    )
    return result.scalars().first()


async def create_media_task_with_file(
    db: AsyncSession, 
    user_id: UUID, 
    original_filename: str, 
    file_path: str
) -> MediaTask:
    """Створення задачі з прив'язаним файлом."""
    db_task = MediaTask(
        id=uuid4(),
        owner_id=user_id,
        original_filename=original_filename,
        storage_path=file_path,
        status=TaskStatus.PENDING
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task