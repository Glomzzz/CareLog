from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional

import bcrypt


@dataclass
class User:
    """Represents a system user with basic authentication and profile metadata."""

    user_id: str
    name: str
    email: str
    password: str
    role: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    is_logged_in: bool = field(default=False, init=False)
    last_login_at: Optional[datetime] = field(default=None, init=False)
    last_logout_at: Optional[datetime] = field(default=None, init=False)

    def login(self, credentials: Dict[str, str]) -> bool:
        """Validate the provided credentials and toggle the in-memory login flag."""
        # We only authenticate active accounts and ensure the password matches.
        if not self.is_active:
            return False

        if credentials.get("email") == self.email:
            # Support both bcrypt-hashed passwords and plain-text passwords used in tests
            try:
                if bcrypt.checkpw(credentials.get("password").encode("utf-8"), self.password.encode("utf-8")):
                    self.is_logged_in = True
                    self.last_login_at = datetime.now()
                    return True
            except (ValueError, TypeError):
                # Not a valid bcrypt hash; fall back to direct string compare
                if credentials.get("password") == self.password:
                    self.is_logged_in = True
                    self.last_login_at = datetime.now()
                    return True
        return False

    def logout(self) -> None:
        """Record a logout event when the user is currently signed in."""
        if self.is_logged_in:
            self.is_logged_in = False
            self.last_logout_at = datetime.now()

    def update_profile(self, updates: Dict[str, Any]) -> bool:
        """Update mutable profile fields from the provided mapping."""
        from app.data.datastore import DataStore
        allowed_fields = {"name", "email", "role"}
        updated = False

        for key, value in updates.items():
            if key in allowed_fields:
                setattr(self, key, value)
                updated = True
        
        if updated:
            DataStore.upsert("users", "userID", self.to_dict())
        return updated

    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change the password when the supplied old password matches."""
        from app.data.datastore import DataStore
        if not new_password:
            return False

        if self.password == old_password:
            self.password = new_password
            DataStore.upsert("users", "userID", self.to_dict())
            return True
        return False

    # -----------------------------
    # Serialization helpers
    # -----------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "userID": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "createdAt": self.created_at.isoformat(),
            "isActive": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        created = data.get("createdAt")
        created_dt = datetime.fromisoformat(created) if isinstance(created, str) else datetime.now()
        return cls(
            user_id=data.get("userID", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=data.get("role", ""),
            created_at=created_dt,
        )
