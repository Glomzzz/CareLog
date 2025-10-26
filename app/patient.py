import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
try:
    from argon2 import PasswordHasher
except ImportError:
    # Provide a lightweight fallback using bcrypt when argon2-cffi is not installed
    import bcrypt

    class PasswordHasher:
        def __init__(self):
            pass

        def hash(self, password: str) -> str:
            # bcrypt returns bytes; decode to str for storage compatibility
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        def verify(self, hashed: str, password: str) -> bool:
            try:
                return bcrypt.checkpw(password.encode(), hashed.encode())
            except Exception:
                return False

class Patient:
    """
    Patient class represents a user in the CareLog system.
    Stores personal information and handles password hashing and PHI encryption.
    """

    def __init__(self, id: str, name: str, email: str, phone: str, password: str = None, password_hash: str = None, key: bytes = None, iv: bytes = None, encrypted: bool = False):
        """
        Initialize a new Patient instance.
        Encrypt PHI fields if not already encrypted.
        Password is hashed using Argon2.
        Validates required fields.
        """
        # Validate required fields
        if not id or not name or not email or not phone:
            raise ValueError("id, name, email, and phone are required fields.")
        if not (password or password_hash):
            raise ValueError("Either password or password_hash must be provided.")

        self.id = id
        # Generate encryption key and IV if not provided
        self.key = key or self.generate_key()
        self.iv = iv or os.urandom(16)
        if encrypted:
            # Fields are already encrypted hex strings
            self.name = name
            self.email = email
            self.phone = phone
        else:
            # Encrypt fields for new registration
            self.name = self.encrypt_field(name)
            self.email = self.encrypt_field(email)
            self.phone = self.encrypt_field(phone)
        # Only hash password if password_hash is not provided
        if password_hash:
            self.password_hash = password_hash
        else:
            self.password_hash = self.hash_password(password)

    def generate_key(self) -> bytes:
        """
        Generate a new AES-256 key for encryption.
        Store this securely in production!
        """
        return os.urandom(32)  # 256 bits (AES-256)

    def encrypt_field(self, value: str) -> str:
        """
        Encrypt a field using AES-256 CBC mode.
        Stores IV with encrypted data for later decryption.
        """
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        # Pad the value to match AES block size using PKCS7
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(value.encode()) + padder.finalize()
        # Encrypt the padded data
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        # Concatenate IV and encrypted data, then encode as hex string
        return (self.iv + encrypted).hex()

    def decrypt_field(self, token: str) -> str:
        """
        Decrypt a field using AES-256 CBC mode.
        Extracts IV from the start of the encrypted data.
        """
        backend = default_backend()
        # Convert hex string back to bytes
        data = bytes.fromhex(token)
        # Extract IV (first 16 bytes) and encrypted data (rest)
        iv = data[:16]
        encrypted = data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        # Decrypt and remove PKCS7 padding
        decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()  # PKCS7 unpadder for AES block size
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted.decode()

    def hash_password(self, password: str) -> str:
        """
        Hash password using Argon2 (for authentication).
        Argon2 is a modern, secure password hashing algorithm.
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        ph = PasswordHasher()
        return ph.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify password using Argon2.
        Returns True if password matches the stored hash, False otherwise.
        """
        ph = PasswordHasher()
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False

    def get_decrypted_name(self) -> str:
        """
        Get the decrypted name of the patient.
        """
        return self.decrypt_field(self.name)

    def get_decrypted_email(self) -> str:
        """
        Get the decrypted email of the patient.
        """
        return self.decrypt_field(self.email)

    def get_decrypted_phone(self) -> str:
        """
        Get the decrypted phone number of the patient.
        """
        return self.decrypt_field(self.phone)

    def __repr__(self):
        """
        Create a string representation of the Patient object.
        Shows decrypted PHI fields for readability.
        """
        return f"Patient(id={self.id}, name={self.get_decrypted_name()}, email={self.get_decrypted_email()}, phone={self.get_decrypted_phone()}, password_hash={self.password_hash})"
    
    def __eq__(self, other):
        """
        Compare two Patient objects for equality.
        Checks all attributes including encrypted fields and password hash.
        """
        if not isinstance(other, Patient):
            return NotImplemented
        return (self.id == other.id and 
                self.name == other.name and 
                self.email == other.email and 
                self.phone == other.phone and
                self.password_hash == other.password_hash)
    
    def to_dict(self):
        """
        Convert Patient instance to dictionary representation.
        Saves key and iv as hex strings for storage.
        """
        return {
            "id": self.id,
            "key": self.key.hex(),  
            "iv": self.iv.hex(),    
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password_hash": self.password_hash
        }
    
    @classmethod
    def patient_from_dict(cls, data: dict):
        """
        Create Patient instance from dictionary representation.
        Loads key and iv from hex strings.
        Validates required fields.
        """
        # Validate required fields in dict
        required = ["id", "name", "email", "phone", "password_hash", "key", "iv"]
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        key = bytes.fromhex(data["key"])
        iv = bytes.fromhex(data["iv"])
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            password_hash=data["password_hash"],  # Use stored hash
            key=key,
            iv=iv,
            encrypted=True  # Indicate fields are already encrypted
        )


