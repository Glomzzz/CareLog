from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.patient import Patient


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
        if not new_status:
            return False
        self.status = new_status
        if new_status == "delivered":
            self.delivered_time = datetime.utcnow()
        return True

    def verify_allergies(self, patient: Patient) -> bool:
        if patient.diet:
            return patient.diet.check_allergies(self.food_items)
        return True

    def record_delivery(self) -> bool:
        if self.status != "delivered":
            return False
        # Nothing to persist yet; return True as an acknowledgement.
        return True

    def handle_special_requests(self, request: str) -> bool:
        if not request:
            return False
        self.special_instructions = request
        return True
