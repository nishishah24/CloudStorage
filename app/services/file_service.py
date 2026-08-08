from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import logger
from app.exceptions.custom_exceptions import (
    FileNotFoundException,
    InvalidFileNameException,
    PermissionDeniedException,
)
from app.models.file import File as FileModel
from app.models.user import User
from app.repositories.file_repository import (
    add_file,
    delete_file_record,
    get_file_by_id,
    list_files_by_owner,
    update_file_name,
)


STORAGE_DIR = Path(settings.storage_path)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def upload_user_file(
    uploaded_file: UploadFile,
    current_user: User,
    db: Session,
) -> FileModel:
    original_name = uploaded_file.filename

    if not original_name:
        raise InvalidFileNameException()

    unique_name = f"{uuid4()}-{original_name}"
    file_path = STORAGE_DIR / unique_name

    file_contents = uploaded_file.file.read()

    try:
        with open(file_path, "wb") as destination:
            destination.write(file_contents)

        file_record = FileModel(
            original_name=original_name,
            stored_name=unique_name,
            file_path=str(file_path),
            content_type=uploaded_file.content_type,
            size=len(file_contents),
            owner_id=current_user.id,
        )

        saved_file = add_file(
            db=db,
            file_record=file_record,
        )

        logger.info(
            "File uploaded successfully. "
            "user_id=%s file_id=%s name=%s size=%s",
            current_user.id,
            saved_file.id,
            saved_file.original_name,
            saved_file.size,
        )

        return saved_file

    except Exception:
        db.rollback()

        if file_path.exists():
            file_path.unlink()

        logger.exception(
            "File upload failed. user_id=%s name=%s",
            current_user.id,
            original_name,
        )

        raise


def get_user_files(
    current_user: User,
    db: Session,
) -> list[FileModel]:
    return list_files_by_owner(
        db=db,
        owner_id=current_user.id,
    )


def get_owned_file(
    file_id: int,
    current_user: User,
    db: Session,
) -> FileModel:
    file_record = get_file_by_id(
        db=db,
        file_id=file_id,
    )

    if file_record is None:
        logger.warning(
            "File access failed because file was not found. "
            "user_id=%s file_id=%s",
            current_user.id,
            file_id,
        )

        raise FileNotFoundException()

    if file_record.owner_id != current_user.id:
        logger.warning(
            "Unauthorized file access attempt. "
            "user_id=%s file_id=%s owner_id=%s",
            current_user.id,
            file_id,
            file_record.owner_id,
        )

        raise PermissionDeniedException()

    return file_record


def rename_user_file(
    file_id: int,
    new_name: str,
    current_user: User,
    db: Session,
) -> FileModel:
    cleaned_name = new_name.strip()

    if not cleaned_name:
        raise InvalidFileNameException()

    file_record = get_owned_file(
        file_id=file_id,
        current_user=current_user,
        db=db,
    )

    old_name = file_record.original_name

    updated_file = update_file_name(
        db=db,
        file_record=file_record,
        new_name=cleaned_name,
    )

    logger.info(
        "File renamed successfully. "
        "user_id=%s file_id=%s old_name=%s new_name=%s",
        current_user.id,
        updated_file.id,
        old_name,
        updated_file.original_name,
    )

    return updated_file


def delete_user_file(
    file_id: int,
    current_user: User,
    db: Session,
) -> None:
    file_record = get_owned_file(
        file_id=file_id,
        current_user=current_user,
        db=db,
    )

    file_path = Path(file_record.file_path)
    original_name = file_record.original_name

    try:
        if file_path.exists():
            file_path.unlink()

        delete_file_record(
            db=db,
            file_record=file_record,
        )

        logger.info(
            "File deleted successfully. "
            "user_id=%s file_id=%s name=%s",
            current_user.id,
            file_id,
            original_name,
        )

    except Exception:
        db.rollback()

        logger.exception(
            "File deletion failed. "
            "user_id=%s file_id=%s name=%s",
            current_user.id,
            file_id,
            original_name,
        )

        raise