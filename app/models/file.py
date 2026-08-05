from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    original_name = Column(String, nullable=False)

    stored_name = Column(String, unique=True, nullable=False)

    file_path = Column(String, nullable=False)

    content_type = Column(String, nullable=True)

    size = Column(Integer, nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )