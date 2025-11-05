from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        """Create parent directory for DATA_FILE and an initial JSON file if missing.

        Note: Use the parent directory of DATA_FILE rather than DATA_DIR so tests can
        override DATA_FILE to point to a temporary location without touching the
        workspace's default data directory. Avoid calling save_all() here to prevent
        recursive ensure/save cycles when the file doesn't yet exist.
        """
        data_dir = Path(cls.DATA_FILE).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        if not Path(cls.DATA_FILE).exists():
            initial = {
                "patients": [],
                "carestaffs": [],
                "notes": [],
                "schedules": [],
            }
            tmp_path = Path(cls.DATA_FILE).with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(initial, f, indent=4, ensure_ascii=False)
            os.replace(tmp_path, cls.DATA_FILE)

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
        # Ensure the target directory exists (but don't call ensure_data_file to avoid recursion)
        Path(cls.DATA_FILE).parent.mkdir(parents=True, exist_ok=True)
        tmp_path = Path(cls.DATA_FILE).with_suffix(".tmp")
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

    # -----------------------------
    # Convenience CRUD helpers
    # -----------------------------
    @classmethod
    def upsert(
        cls, collection: str, id_key: str, item: Dict[str, Any]
    ) -> None:
        """Insert or update an object in a collection keyed by `id_key`.

        If an object with the same id exists, it is replaced; otherwise, it is appended.
        """
        data = cls.load_all()
        items = data.setdefault(collection, [])
        key = item.get(id_key)
        if key is None:
            # If the id is missing, just append as-is.
            items.append(item)
            cls.save_all(data)
            return
        for i, existing in enumerate(items):
            if isinstance(existing, dict) and existing.get(id_key) == key:
                items[i] = item
                cls.save_all(data)
                return
        items.append(item)
        cls.save_all(data)

    @classmethod
    def get_by_id(
        cls, collection: str, id_key: str, id_value: Any
    ) -> Optional[Dict[str, Any]]:
        items = cls.get_collection(collection)
        for item in items:
            if isinstance(item, dict) and item.get(id_key) == id_value:
                return item
        return None

    @classmethod
    def delete_by_id(
        cls, collection: str, id_key: str, id_value: Any
    ) -> bool:
        data = cls.load_all()
        items = data.setdefault(collection, [])
        new_items = [it for it in items if not (isinstance(it, dict) and it.get(id_key) == id_value)]
        changed = len(new_items) != len(items)
        if changed:
            data[collection] = new_items
            cls.save_all(data)
        return changed
