import os
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class WellbeingLog:
    def __init__(self, id: str, patient_id: str, timestamp: datetime,
                 pain_level: int, mood: str, appetite: str, notes: str,
                 key: bytes = None, iv: bytes = None, encrypted: bool = False):
        """
        Initialize a new WellbeingLog instance.
        Validates required fields and encrypts PHI if needed.
        """
        # Validate required fields
        if not id:
            raise ValueError("id is required.")
        if not patient_id:
            raise ValueError("patient_id is required.")
        if not timestamp:
            raise ValueError("timestamp is required.")
        if pain_level is None or pain_level == "":
            raise ValueError("pain_level is required.")
        if mood is None or mood == "":
            raise ValueError("mood is required.")
        if appetite is None or appetite == "":
            raise ValueError("appetite is required.")
        if notes is None or notes == "":
            raise ValueError("notes is required.")

        self.id = id
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.key = key or self.generate_key()
        self.iv = iv or os.urandom(16)
        if encrypted:
            # Fields are already encrypted hex strings
            self.pain_level = pain_level
            self.mood = mood
            self.appetite = appetite
            self.notes = notes
        else:
            # Encrypt fields for new log entry
            self.pain_level = self.encrypt_field(str(pain_level))
            self.mood = self.encrypt_field(mood)
            self.appetite = self.encrypt_field(appetite)
            self.notes = self.encrypt_field(notes)

    def generate_key(self) -> bytes:
        """
        Generate a new AES-256 key for encryption.
        """
        return os.urandom(32)  # AES-256

    def encrypt_field(self, value: str) -> str:
        """
        Encrypt a field using AES-256 CBC mode.
        Stores IV with encrypted data for later decryption.
        """
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(value.encode()) + padder.finalize()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return (self.iv + encrypted).hex()

    def decrypt_field(self, token: str) -> str:
        """
        Decrypt a field using AES-256 CBC mode.
        Extracts IV from the start of the encrypted data.
        """
        backend = default_backend()
        data = bytes.fromhex(token)
        iv = data[:16]
        encrypted = data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted.decode()

    def get_decrypted_pain_level(self) -> int:
        """
        Decrypt and return pain level as integer.
        """
        decrypted = self.decrypt_field(self.pain_level)
        if not decrypted.isdigit():
            raise ValueError("Decrypted pain level is not a valid integer.")
        return int(decrypted)

    def get_decrypted_mood(self) -> str:
        """
        Decrypt and return mood.
        """
        return self.decrypt_field(self.mood)

    def get_decrypted_appetite(self) -> str:
        """
        Decrypt and return appetite.
        """
        return self.decrypt_field(self.appetite)

    def get_decrypted_notes(self) -> str:
        """
        Decrypt and return notes.
        """
        return self.decrypt_field(self.notes)

    def to_dict(self):
        """
        Convert WellbeingLog instance to dictionary representation.
        Saves key and iv as hex strings for storage.
        """
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "timestamp": str(self.timestamp),
            "key": self.key.hex(),
            "iv": self.iv.hex(),
            "pain_level": self.pain_level,
            "mood": self.mood,
            "appetite": self.appetite,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create WellbeingLog instance from dictionary representation.
        Loads key and iv from hex strings.
        Validates required fields.
        """
        required = ["id", "patient_id", "timestamp", "pain_level", "mood", "appetite", "notes", "key", "iv"]
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        key = bytes.fromhex(data["key"])
        iv = bytes.fromhex(data["iv"])
        return cls(
            id=data["id"],
            patient_id=data["patient_id"],
            timestamp=data["timestamp"],
            pain_level=data["pain_level"],
            mood=data["mood"],
            appetite=data["appetite"],
            notes=data["notes"],
            key=key,
            iv=iv,
            encrypted=True
        )

    def __repr__(self):
        """
        Create a string representation of the WellbeingLog object.
        Shows decrypted PHI fields for readability.
        """
        return (f"WellbeingLog(id={self.id}, patient_id={self.patient_id}, timestamp={self.timestamp}, "
                f"pain_level={self.get_decrypted_pain_level()}, mood={self.get_decrypted_mood()}, "
                f"appetite={self.get_decrypted_appetite()}, notes={self.get_decrypted_notes()})")

    def __eq__(self, other):
        """
        Compare two WellbeingLog objects for equality.
        Checks all attributes including encrypted fields.
        """
        if not isinstance(other, WellbeingLog):
            return NotImplemented
        return (self.id == other.id and
                self.patient_id == other.patient_id and
                self.timestamp == other.timestamp and
                self.pain_level == other.pain_level and
                self.mood == other.mood and
                self.appetite == other.appetite and
                self.notes == other.notes)
