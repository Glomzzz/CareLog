from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class FoodToDeliver:
    """Tracks a single meal delivery for auditing and follow-up."""

    delivery_id: str
    food_items: str
    room_number: int
    scheduled_time: datetime
    delivered_time: Optional[datetime] = None
    status: str = "scheduled"
    special_instructions: str = ""

    def update_delivery_status(self, new_status: str) -> bool:
        from app.datastore import DataStore
        if not new_status:
            return False
        self.status = new_status
        if new_status == "delivered":
            self.delivered_time = datetime.now()
        DataStore.upsert("food_deliveries", "deliveryID", self.to_dict())
        return True

    def verify_allergies(self, patient) -> bool:
        if patient.diet:
            return patient.diet.check_allergies(self.food_items)
        return True

    def record_delivery(self) -> bool:
        if self.status != "delivered":
            return False
        # Nothing to persist yet; return True as an acknowledgement.
        return True

    def handle_special_requests(self, request: str) -> bool:
        from app.datastore import DataStore
        if not request:
            return False
        self.special_instructions = request
        DataStore.upsert("food_deliveries", "deliveryID", self.to_dict())
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deliveryID": self.delivery_id,
            "foodItems": self.food_items,
            "roomNumber": self.room_number,
            "scheduledTime": self.scheduled_time.isoformat(),
            "deliveredTime": self.delivered_time.isoformat() if self.delivered_time else None,
            "status": self.status,
            "specialInstructions": self.special_instructions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FoodToDeliver":
        return cls(
            delivery_id=data.get("deliveryID", ""),
            food_items=data.get("foodItems", ""),
            room_number=int(data.get("roomNumber", 0)),
            scheduled_time=datetime.fromisoformat(data.get("scheduledTime")) if data.get("scheduledTime") else datetime.now(),
            delivered_time=datetime.fromisoformat(data.get("deliveredTime")) if data.get("deliveredTime") else None,
            status=data.get("status", "scheduled"),
            special_instructions=data.get("specialInstructions", ""),
        )
