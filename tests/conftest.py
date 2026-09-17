import os
import shutil
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["STORAGE_PATH"] = "test_storage"

from app.database.database import Base
from app.database.dependencies import get_db
from app.main import app

TEST_DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'cloud_user')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'password123')}@"
    f"{os.getenv('POSTGRES_HOST', '127.0.0.1')}:"
    f"{os.getenv('POSTGRES_PORT', '5433')}/"
    f"{os.getenv('POSTGRES_DB', 'cloud_file_storage_test')}"
)

test_engine = create_engine(
    TEST_DATABASE_URL,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

_mock_firebase_storage_data = {}


def _mock_upload(file_bytes, blob_name, content_type=None):
    _mock_firebase_storage_data[blob_name] = file_bytes
    return blob_name


def _mock_download(blob_name):
    return _mock_firebase_storage_data.get(blob_name, b"")


def _mock_delete(blob_name):
    _mock_firebase_storage_data.pop(blob_name, None)


@pytest.fixture(autouse=True)
def mock_firebase_storage_calls(monkeypatch):
    _mock_firebase_storage_data.clear()
    monkeypatch.setattr("app.services.file_service.upload_file_to_firebase", _mock_upload)
    monkeypatch.setattr("app.services.file_service.download_file_bytes_from_firebase", _mock_download)
    monkeypatch.setattr("app.services.file_service.delete_file_from_firebase", _mock_delete)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def setup_test_database():
    Base.metadata.create_all(
        bind=test_engine,
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine,
    )

    test_storage = Path("test_storage")

    if test_storage.exists():
        shutil.rmtree(test_storage)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(
        bind=connection,
    )

    try:
        yield session

    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[
        get_db
    ] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()