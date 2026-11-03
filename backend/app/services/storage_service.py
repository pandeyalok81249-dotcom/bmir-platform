import os
from pathlib import Path
from typing import Optional
from app.core.config import settings


class StorageService:
    def __init__(self):
        self.base_path = Path(settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_file(self, user_id: str, filename: str, content: bytes) -> str:
        user_dir = self.base_path / "users" / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        file_path = user_dir / safe_filename

        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path.relative_to(self.base_path))

    def read_file(self, storage_key: str) -> Optional[bytes]:
        full_path = self.base_path / storage_key
        if not full_path.exists():
            return None
        with open(full_path, "rb") as f:
            return f.read()

    def delete_file(self, storage_key: str) -> bool:
        full_path = self.base_path / storage_key
        if full_path.exists():
            full_path.unlink()
            return True
        return False

