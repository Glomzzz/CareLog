from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from app.carestaff import CareStaff
    from app.patient import Patient


@dataclass
class Task:
    """Actionable item assigned to a member of the care team."""

    task_id: str
    title: str
    description: str
    priority: str
    status: str
    due_date: datetime
    completed_at: Optional[datetime] = None
    assignee_id: Optional[str] = None

    def assign_task(self, assignee: "CareStaff") -> bool:
        from app.carestaff import CareStaff

        if not isinstance(assignee, CareStaff):
            return False
        self.assignee_id = assignee.staff_id
        assignee.tasks.append(self)
        return True

    def update_progress(self, progress: str) -> bool:
        if not progress:
            return False
        self.status = progress
        return True

    def mark_complete(self) -> bool:
        self.status = "completed"
        self.completed_at = datetime.now()
        return True

    def escalate_task(self) -> bool:
        self.priority = "high"
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "taskID": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "dueDate": self.due_date.isoformat(),
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "assigneeID": self.assignee_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            task_id=data.get("taskID", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=data.get("priority", "normal"),
            status=data.get("status", "pending"),
            due_date=datetime.fromisoformat(data.get("dueDate")) if data.get("dueDate") else datetime.now(),
        )


class Schedule:
    """Represents a scheduled activity for a member of the care staff."""

    def __init__(
        self,
        carestaff_id: str,
        task: str,
        date: str,
        *,
        schedule_id: Optional[str] = None,
        purpose: Optional[str] = None,
        priority: str = "normal",
        location: str = "",
        date_and_time: Optional[datetime] = None,
        estimated_duration: int = 0,
        recurrence: str = "none",
    ) -> None:
        self.carestaff_id = carestaff_id
        self.task = task
        self.date = date  # Backward compatibility for CLI JSON dumps
        self.schedule_id = schedule_id or f"sch-{carestaff_id}-{hash(task) & 0xffff}"
        self.purpose = purpose or task
        self.priority = priority
        self.location = location
        self.date_and_time = date_and_time or self._parse_date(date)
        self.estimated_duration = estimated_duration
        self.recurrence = recurrence
        self.staff_list: List[str] = []

    def _parse_date(self, date_value: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(date_value)
        except (TypeError, ValueError):
            return None

    def update_purpose(self, new_purpose: str) -> bool:
        if not new_purpose:
            return False
        self.purpose = new_purpose
        return True

    def update_staff(self, staff_list: List["CareStaff"]) -> bool:
        if staff_list is None:
            return False
        self.staff_list = [staff.staff_id for staff in staff_list]
        return True

    def update_location(self, new_location: str) -> bool:
        if not new_location:
            return False
        self.location = new_location
        return True

    def update_date_and_time(self, new_datetime: datetime) -> bool:
        if not isinstance(new_datetime, datetime):
            return False
        self.date_and_time = new_datetime
        self.date = new_datetime.date().isoformat()
        return True

    def check_availability(self) -> bool:
        """In-memory availability check placeholder."""
        return bool(self.date_and_time)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the schedule with legacy-friendly keys."""
        return {
            "carestaffID": self.carestaff_id,
            "task": self.task,
            "date": self.date,
            "scheduleID": self.schedule_id,
            "purpose": self.purpose,
            "priority": self.priority,
            "location": self.location,
            "recurrence": self.recurrence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Schedule":
        return cls(
            carestaff_id=data.get("carestaffID", ""),
            task=data.get("task", ""),
            date=data.get("date", ""),
            schedule_id=data.get("scheduleID"),
            purpose=data.get("purpose"),
            priority=data.get("priority", "normal"),
            location=data.get("location", ""),
            date_and_time=datetime.fromisoformat(data.get("dateAndTime")) if data.get("dateAndTime") else None,
            estimated_duration=int(data.get("estimatedDuration", 0)),
            recurrence=data.get("recurrence", "none"),
        )


@dataclass
class Appointment:
    """Captures an appointment request initiated by the patient."""

    appointment_id: str
    patient_id: str
    date_and_time: datetime
    type: str
    status: str = "requested"
    notes: str = ""
    duration: int = 30
    staff_id: Optional[str] = None

    @classmethod
    def create_from_preferences(cls, patient: "Patient", preferences: Dict[str, Any]) -> "Appointment":
        preferred_time = preferences.get("date_and_time", datetime.now())
        appointment_type = preferences.get("type", "consultation")
        return cls(
            appointment_id=f"appt-{patient.patient_id}-{int(datetime.now().timestamp())}",
            patient_id=patient.patient_id,
            date_and_time=preferred_time,
            type=appointment_type,
            notes=preferences.get("notes", ""),
            duration=preferences.get("duration", 30),
        )

    def change_date_or_time(self, new_datetime: datetime) -> bool:
        if not isinstance(new_datetime, datetime):
            return False
        self.date_and_time = new_datetime
        return True

    def change_staff(self, staff_member: "CareStaff") -> bool:
        from app.carestaff import CareStaff

        if not isinstance(staff_member, CareStaff):
            return False
        self.staff_id = staff_member.staff_id
        return True

    def send_reminders(self) -> bool:
        return True

    def check_conflicts(self) -> List["Appointment"]:
        # Conflict detection is out of scope; return an empty list for now.
        return []

    def reschedule(self, new_datetime: datetime) -> bool:
        return self.change_date_or_time(new_datetime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "appointmentID": self.appointment_id,
            "patientID": self.patient_id,
            "dateAndTime": self.date_and_time.isoformat(),
            "type": self.type,
            "status": self.status,
            "notes": self.notes,
            "duration": self.duration,
            "staffID": self.staff_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Appointment":
        return cls(
            appointment_id=data.get("appointmentID", ""),
            patient_id=data.get("patientID", ""),
            date_and_time=datetime.fromisoformat(data.get("dateAndTime")) if data.get("dateAndTime") else datetime.now(),
            type=data.get("type", "consultation"),
            status=data.get("status", "requested"),
            notes=data.get("notes", ""),
            duration=int(data.get("duration", 30)),
            staff_id=data.get("staffID"),
        )
