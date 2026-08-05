from sqlalchemy.orm import Session

from app.models.file import File as FileModel


def add_file(
    db: Session,
    file_record: FileModel,
) -> FileModel:
    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return file_record


def get_file_by_id(
    db: Session,
    file_id: int,
) -> FileModel | None:
    return (
        db.query(FileModel)
        .filter(FileModel.id == file_id)
        .first()
    )


def list_files_by_owner(
    db: Session,
    owner_id: int,
) -> list[FileModel]:
    return (
        db.query(FileModel)
        .filter(FileModel.owner_id == owner_id)
        .order_by(FileModel.created_at.desc())
        .all()
    )


def delete_file_record(
    db: Session,
    file_record: FileModel,
) -> None:
    db.delete(file_record)
    db.commit()

def update_file_name(
    db: Session,
    file_record: FileModel,
    new_name: str,
) -> FileModel:
    file_record.original_name = new_name

    db.commit()
    db.refresh(file_record)

    return file_record