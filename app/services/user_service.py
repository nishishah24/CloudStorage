from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.exceptions.custom_exceptions import (
    DuplicateUserException,
    InvalidCredentialsException,
    PermissionDeniedException,
)
from app.models.user import User
from app.repositories.user_repository import (
    add_user,
    get_user_by_email,
)
from app.schemas.user import UserCreate, UserLogin


def create_user(
    user_data: UserCreate,
    db: Session,
) -> User:
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    try:
        return add_user(
            db=db,
            user=new_user,
        )

    except IntegrityError:
        db.rollback()
        raise DuplicateUserException()


def authenticate_user(
    login_data: UserLogin,
    db: Session,
) -> str:
    db_user = get_user_by_email(
        db=db,
        email=login_data.email,
    )

    if db_user is None:
        raise InvalidCredentialsException()

    if not verify_password(
        login_data.password,
        db_user.hashed_password,
    ):
        raise InvalidCredentialsException()

    if not db_user.is_active:
        raise PermissionDeniedException()

    return create_access_token(
        data={"sub": db_user.email}
    )