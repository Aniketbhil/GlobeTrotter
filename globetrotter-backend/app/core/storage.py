import os
import uuid
from pathlib import Path
from typing import Protocol

from fastapi import UploadFile

from app.common.exceptions import BadRequestException, PayloadTooLargeException
from app.core.config import settings


class StorageBackend(Protocol):
    async def save(self, file: UploadFile, subfolder: str = "photos") -> str: ...

    def url_for(self, relative_path: str) -> str: ...

    def delete(self, relative_path: str) -> None: ...


class LocalDiskStorage:
    def __init__(
        self,
        upload_dir: str = settings.UPLOAD_DIR,
        max_size_mb: int = settings.MAX_UPLOAD_SIZE_MB,
        allowed_types: list[str] | None = None,
        public_base_url: str = settings.PUBLIC_BASE_URL,
    ):
        self.upload_dir = upload_dir
        self.max_bytes = max_size_mb * 1024 * 1024
        self.allowed_types = allowed_types or settings.ALLOWED_IMAGE_CONTENT_TYPES
        self.public_base_url = public_base_url.rstrip("/")

    async def save(self, file: UploadFile, subfolder: str = "photos") -> str:
        if file.content_type not in self.allowed_types:
            raise BadRequestException(
                f"Content type '{file.content_type}' is not allowed. Allowed"
                f" types: {', '.join(self.allowed_types)}"
            )

        target_dir = Path("uploads") / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        original_ext = Path(file.filename or "").suffix.lower()
        if not original_ext:
            if file.content_type == "image/jpeg":
                original_ext = ".jpg"
            elif file.content_type == "image/png":
                original_ext = ".png"
            elif file.content_type == "image/webp":
                original_ext = ".webp"
            else:
                original_ext = ".bin"

        unique_filename = f"{uuid.uuid4().hex}{original_ext}"
        file_path = target_dir / unique_filename

        total_bytes = 0
        chunk_size = 1024 * 64

        with open(file_path, "wb") as out_file:  # noqa: ASYNC230
            while chunk := await file.read(chunk_size):
                total_bytes += len(chunk)
                if total_bytes > self.max_bytes:
                    out_file.close()
                    if file_path.exists():
                        os.remove(file_path)
                    raise PayloadTooLargeException(
                        f"File size exceeds maximum allowed size of"
                        f" {settings.MAX_UPLOAD_SIZE_MB}MB"
                    )
                out_file.write(chunk)

        await file.seek(0)
        relative_path = f"uploads/{subfolder}/{unique_filename}"
        return relative_path

    def url_for(self, relative_path: str) -> str:
        clean_path = relative_path.lstrip("/")
        return f"{self.public_base_url}/{clean_path}"

    def delete(self, relative_path: str) -> None:
        if not relative_path:
            return

        clean_path = relative_path
        if self.public_base_url in clean_path:
            clean_path = clean_path.replace(f"{self.public_base_url}/", "")
        clean_path = clean_path.lstrip("/")

        path_on_disk = Path(clean_path)
        if path_on_disk.exists() and path_on_disk.is_file():
            try:
                os.remove(path_on_disk)
            except OSError:
                pass


def get_storage() -> StorageBackend:
    return LocalDiskStorage()
