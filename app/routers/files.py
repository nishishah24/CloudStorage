from fastapi import (
    APIRouter,
    Depends,
    File,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.file import (
    FileRename,
    FileRenameResponse,
    FileResponse,
    MessageResponse,
)
from app.services.file_service import (
    delete_user_file,
    download_user_file_content,
    get_user_files,
    rename_user_file,
    upload_user_file,
)


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post(
    "/upload",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    uploaded_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upload_user_file(
        uploaded_file=uploaded_file,
        current_user=current_user,
        db=db,
    )


@router.get(
    "",
    response_model=list[FileResponse],
)
def list_my_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_files(
        current_user=current_user,
        db=db,
    )


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes, file_record = download_user_file_content(
        file_id=file_id,
        current_user=current_user,
        db=db,
    )

    return Response(
        content=file_bytes,
        media_type=file_record.content_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file_record.original_name}"'
        },
    )


@router.patch(
    "/{file_id}/rename",
    response_model=FileRenameResponse,
)
def rename_file(
    file_id: int,
    rename_data: FileRename,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return rename_user_file(
        file_id=file_id,
        new_name=rename_data.new_name,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/{file_id}",
    response_model=MessageResponse,
)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_user_file(
        file_id=file_id,
        current_user=current_user,
        db=db,
    )

    return {
        "message": "File deleted successfully",
    }