import json
import os
from typing import Any

class StorageService:
    def __init__(self, data_dir: str = "data"):
        # Use project root for data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_file_path(self, name: str) -> str:
        # Get the full path to the JSON file in the project root data folder
        return os.path.join(self.data_dir, f"{name}.json")

    def save(self, name: str, data: Any) -> None:
        """
        Save data to the JSON file with pretty formatting.
        """
        with open(self._get_file_path(name), 'w') as f:
            json.dump(data, f, default=str, indent=4)  # Pretty JSON output

    def load(self, name: str) -> Any:
        """
        Load data from the JSON file.
        Returns an empty dict if file does not exist.
        """
        try:
            with open(self._get_file_path(name), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
