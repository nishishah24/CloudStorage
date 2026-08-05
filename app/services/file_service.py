from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.file import File as FileModel
from app.models.user import User
from app.repositories.file_repository import (
    add_file,
    delete_file_record,
    get_file_by_id,
    list_files_by_owner,
    update_file_name,
)

STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)


def upload_user_file(
    uploaded_file: UploadFile,
    current_user: User,
    db: Session,
) -> FileModel:
    original_name = uploaded_file.filename

    if not original_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename",
        )

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

        return add_file(
            db=db,
            file_record=file_record,
        )

    except Exception:
        db.rollback()

        if file_path.exists():
            file_path.unlink()

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_record.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this file",
        )

    return file_record


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

    if file_path.exists():
        file_path.unlink()

    delete_file_record(
        db=db,
        file_record=file_record,
    )

def rename_user_file(
    file_id: int,
    new_name: str,
    current_user: User,
    db: Session,
) -> FileModel:
    cleaned_name = new_name.strip()

    if not cleaned_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name cannot be empty",
        )

    file_record = get_owned_file(
        file_id=file_id,
        current_user=current_user,
        db=db,
    )

    return update_file_name(
        db=db,
        file_record=file_record,
        new_name=cleaned_name,
    )