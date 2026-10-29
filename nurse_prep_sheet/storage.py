"""Local JSON storage for the Nurse Shift Prep Sheet.

All data is stored as plain JSON files on the local machine. No data is
sent anywhere, and no account or network access is required.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .models import ShiftSheet

DEFAULT_STORAGE_DIR = Path.home() / ".nurse-prep-sheet"
DEFAULT_FILE_NAME = "shift.json"


class StorageError(Exception):
    """Raised when reading or writing the local storage file fails."""


def default_storage_path() -> Path:
    """Return the default path for the shift data file."""
    return DEFAULT_STORAGE_DIR / DEFAULT_FILE_NAME


def load_sheet(path: Path | str) -> ShiftSheet:
    """Load a shift sheet from a JSON file.

    Returns an empty sheet when the file does not exist yet.
    """
    path = Path(path)
    if not path.exists():
        return ShiftSheet()
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise StorageError(f"failed to read storage file {path}: {exc}") from exc
    try:
        return ShiftSheet.from_dict(data)
    except (KeyError, TypeError) as exc:
        raise StorageError(f"failed to parse storage file {path}: {exc}") from exc


def save_sheet(sheet: ShiftSheet, path: Path | str) -> None:
    """Save a shift sheet to a JSON file, creating folders as needed."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(sheet.to_dict(), handle, indent=2, sort_keys=True)
            handle.write("\n")
    except OSError as exc:
        raise StorageError(f"failed to write storage file {path}: {exc}") from exc


def resolve_storage_path(env_value: Optional[str]) -> Path:
    """Resolve the storage path from an environment variable or default."""
    if env_value:
        return Path(env_value)
    return default_storage_path()
