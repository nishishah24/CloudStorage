from datetime import datetime

from pydantic import BaseModel, Field


class FileRename(BaseModel):
    new_name: str = Field(
        min_length=1,
        max_length=255,
    )


class FileResponse(BaseModel):
    id: int
    original_name: str
    content_type: str | None
    size: int
    owner_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class FileRenameResponse(BaseModel):
    id: int
    original_name: str
    stored_name: str

    model_config = {
        "from_attributes": True,
    }


class MessageResponse(BaseModel):
    message: str