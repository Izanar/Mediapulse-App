import uuid
import enum
from pydantic import BaseModel, ConfigDict
from app.models import TaskStatus

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- MediaTask Schemas ---
class MediaTaskBase(BaseModel):
    original_filename: str
    is_public: bool = False

class MediaTaskCreate(MediaTaskBase):
    pass

class MediaTaskResponse(MediaTaskBase):
    id: uuid.UUID
    storage_path: str
    processed_path: str | None = None
    status: TaskStatus
    owner_id: uuid.UUID | None = None

    model_config = ConfigDict(from_attributes=True)