import os
from pathlib import Path

from backend.config import UPLOAD_DIR, EXPORT_DIR


def save_upload(file_storage, subdir=""):
    base = Path(UPLOAD_DIR)
    if subdir:
        base = base / subdir
    base.mkdir(parents=True, exist_ok=True)
    path = base / file_storage.filename
    file_storage.save(str(path))
    return path, path.stat().st_size


def resolve_file_path(relative_path):
    base = Path(UPLOAD_DIR)
    full = base / relative_path
    if full.exists():
        return full
    return None


def get_file_stream(relative_path):
    path = resolve_file_path(relative_path)
    if path is None:
        return None, None
    try:
        return open(path, "rb"), path.name
    except OSError:
        return None, None
