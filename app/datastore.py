from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class DataStore:
    """Simple JSON-backed data store for the CareLog app.

    Default file: data/carelog_data.json. Tests or CLI can override the
    `DATA_FILE` attribute if they need a different file (e.g. test fixtures).
    Provides convenience helpers to read/update named collections stored as
    top-level keys in the JSON file.
    """

    DATA_DIR = Path("data")
    DATA_FILE = DATA_DIR / "carelog_data.json"

    @classmethod
    def ensure_data_file(cls) -> None:
        """Create data directory and an empty data file with sane defaults if missing."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not cls.DATA_FILE.exists():
            initial = {"patients": [], "carestaffs": [], "notes": [], "schedules": []}
            cls.save_all(initial)

    @classmethod
    def load_all(cls) -> Dict[str, Any]:
        """Load and return the entire JSON data structure.

        Returns an in-memory dict. The caller should not mutate the returned
        dict if it intends to persist changes; use the provided helpers.
        """
        cls.ensure_data_file()
        with open(cls.DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def save_all(cls, data: Dict[str, Any]) -> None:
        """Persist the provided dict to the data file atomically.

        The implementation writes to a temporary file then renames it to avoid
        truncation on unexpected failures.
        """
        cls.ensure_data_file()
        tmp_path = cls.DATA_FILE.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, cls.DATA_FILE)

    @classmethod
    def get_collection(cls, name: str) -> List[Any]:
        data = cls.load_all()
        return data.get(name, [])

    @classmethod
    def set_collection(cls, name: str, values: List[Any]) -> None:
        data = cls.load_all()
        data[name] = values
        cls.save_all(data)

    @classmethod
    def append_to_collection(cls, name: str, item: Any) -> None:
        data = cls.load_all()
        data.setdefault(name, []).append(item)
        cls.save_all(data)
