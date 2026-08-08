from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import (
    DuplicateUserException,
    FileNotFoundException,
    InvalidCredentialsException,
    InvalidFileNameException,
    PermissionDeniedException,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(FileNotFoundException)
    async def file_not_found_handler(
        request: Request,
        exc: FileNotFoundException,
    ):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": exc.message,
            },
        )

    @app.exception_handler(PermissionDeniedException)
    async def permission_denied_handler(
        request: Request,
        exc: PermissionDeniedException,
    ):
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": exc.message,
            },
        )

    @app.exception_handler(DuplicateUserException)
    async def duplicate_user_handler(
        request: Request,
        exc: DuplicateUserException,
    ):
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": exc.message,
            },
        )

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsException,
    ):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": exc.message,
            },
        )

    @app.exception_handler(InvalidFileNameException)
    async def invalid_file_name_handler(
        request: Request,
        exc: InvalidFileNameException,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": exc.message,
            },
        )