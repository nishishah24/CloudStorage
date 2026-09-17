import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, storage

from app.core.config import BASE_DIR, settings
from app.core.logger import logger

_firebase_app = None


def get_firebase_bucket():
    global _firebase_app
    if not _firebase_app:
        if not firebase_admin._apps:
            cred = None

            # Option A: JSON string from Environment Variable (for Vercel deployment)
            if settings.firebase_credentials_json:
                try:
                    cred_dict = json.loads(settings.firebase_credentials_json)
                    cred = credentials.Certificate(cred_dict)
                except Exception as err:
                    logger.error("Failed to parse FIREBASE_CREDENTIALS_JSON: %s", err)

            # Option B: JSON File Path on Local Disk
            if cred is None:
                cred_setting = settings.firebase_credentials_path
                cred_path = Path(cred_setting) if cred_setting else Path("serviceAccountKey.json")

                if not cred_path.is_absolute():
                    cred_path = BASE_DIR / cred_path

                if cred_path.exists():
                    cred = credentials.Certificate(str(cred_path))
                else:
                    logger.warning(
                        "Firebase credentials file not found at %s. Attempting default init.",
                        cred_path,
                    )
                    cred = credentials.AnonymousCredentials()

            _firebase_app = firebase_admin.initialize_app(
                cred,
                {
                    "storageBucket": settings.firebase_storage_bucket,
                },
            )
        else:
            _firebase_app = firebase_admin.get_app()

    return storage.bucket(app=_firebase_app)


def upload_file_to_firebase(
    file_bytes: bytes, blob_name: str, content_type: str | None = None
) -> str:
    bucket = get_firebase_bucket()
    blob = bucket.blob(blob_name)
    blob.upload_from_string(
        file_bytes,
        content_type=content_type or "application/octet-stream",
    )
    return blob_name


def download_file_bytes_from_firebase(blob_name: str) -> bytes:
    bucket = get_firebase_bucket()
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def delete_file_from_firebase(blob_name: str) -> None:
    bucket = get_firebase_bucket()
    blob = bucket.blob(blob_name)
    if blob.exists():
        blob.delete()
