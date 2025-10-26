from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class PatientAssignment:
    """Represents the linkage between a patient and a care staff member."""

    assignment_id: str
    assigned_date: date
    assignment_type: str
    notes: str = ""
    patient_id: Optional[str] = None
    staff_id: Optional[str] = None
    active: bool = True

    def assign_patient(self, patient_id: str, staff_id: str) -> bool:
        from app.datastore import DataStore
        if not patient_id or not staff_id:
            return False
        self.patient_id = patient_id
        self.staff_id = staff_id
        self.active = True
        DataStore.upsert("assignments", "assignmentID", self.to_dict())
        return True

    def transfer_patient(self, patient_id: str, new_staff_id: str) -> bool:
        from app.datastore import DataStore
        if patient_id != self.patient_id:
            return False
        self.staff_id = new_staff_id
        DataStore.upsert("assignments", "assignmentID", self.to_dict())
        return True

    def end_assignment(self, patient_id: str) -> bool:
        from app.datastore import DataStore
        if patient_id != self.patient_id:
            return False
        self.active = False
        DataStore.upsert("assignments", "assignmentID", self.to_dict())
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assignmentID": self.assignment_id,
            "assignedDate": self.assigned_date.isoformat(),
            "assignmentType": self.assignment_type,
            "notes": self.notes,
            "patientID": self.patient_id,
            "staffID": self.staff_id,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientAssignment":
        return cls(
            assignment_id=data.get("assignmentID", ""),
            assigned_date=date.fromisoformat(data.get("assignedDate")) if data.get("assignedDate") else date.today(),
            assignment_type=data.get("assignmentType", ""),
            notes=data.get("notes", ""),
            patient_id=data.get("patientID"),
            staff_id=data.get("staffID"),
            active=bool(data.get("active", True)),
        )
