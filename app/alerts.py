from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from app.user import User


@dataclass
class Alert:
    """System generated alert notifying care staff of key events."""

    alert_id: str
    type: str
    severity: str
    message: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    status: str = "open"

    def acknowledge_alert(self, user: User) -> bool:
        if self.status == "open":
            self.status = "acknowledged"
            self.acknowledged_at = datetime.utcnow()
            return True
        return False

    def resolve_alert(self, user: User) -> bool:
        if self.status in {"open", "acknowledged"}:
            self.status = "resolved"
            self.resolved_at = datetime.utcnow()
            return True
        return False

    def escalate_alert(self) -> bool:
        if self.status != "resolved":
            self.severity = "critical"
            return True
        return False

    def calculate_priority(self) -> str:
        """Derive a string priority label based on severity."""
        mapping = {"low": "P3", "medium": "P2", "high": "P1", "critical": "P0"}
        return mapping.get(self.severity.lower(), "P3")


@dataclass
class NotificationService:
    """Small in-memory notification delivery orchestrator."""

    service_id: str
    channels: List[str]
    user_preferences: Dict[str, Dict[str, str]] = field(default_factory=dict)
    sent_notifications: List[Dict[str, str]] = field(default_factory=list)

    def send_immediate_alert(self, user: User, message: str) -> bool:
        if not message:
            return False
        payload = {
            "user_id": user.user_id,
            "message": message,
            "channel": self._preferred_channel(user.user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.sent_notifications.append(payload)
        return True

    def send_scheduled_reminder(self, user: User, message: str, time: datetime) -> bool:
        payload = {
            "user_id": user.user_id,
            "message": message,
            "scheduled_for": time.isoformat(),
            "channel": self._preferred_channel(user.user_id),
        }
        self.sent_notifications.append(payload)
        return True

    def batch_notify(self, users: List[User], message: str) -> bool:
        for user in users:
            self.send_immediate_alert(user, message)
        return True

    def track_delivery(self, notification_id: str) -> Dict[str, str]:
        """Return a naive delivery receipt matching the supplied identifier."""
        for record in self.sent_notifications:
            if record.get("timestamp", "").endswith(notification_id):
                return record
        return {}

    def _preferred_channel(self, user_id: str) -> str:
        preferences = self.user_preferences.get(user_id, {})
        return preferences.get("channel", self.channels[0] if self.channels else "email")
