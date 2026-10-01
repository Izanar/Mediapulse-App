import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models import TaskStatus


# --- Схемы для Пользователя (User) ---
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Схемы для Авторизации / Токенов ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# --- Схемы для Задач (MediaTask) ---
class MediaTaskBase(BaseModel):
    original_filename: str
    is_public: bool = False


class MediaTaskCreate(MediaTaskBase):
    pass


class MediaTaskResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    storage_path: str
    processed_path: Optional[str] = None
    status: TaskStatus
    is_public: bool
    owner_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)