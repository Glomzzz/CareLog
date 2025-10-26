from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class MedicalRecord:
    """Base record storing generic metadata shared by all medical entries."""

    record_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    history: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Default timestamps to now when not explicitly provided.
        now = datetime.utcnow()
        if not isinstance(self.created_at, datetime):
            self.created_at = now
        if not isinstance(self.updated_at, datetime):
            self.updated_at = self.created_at

    def get_history(self) -> List[Dict[str, str]]:
        """Return a shallow copy of the change log for display purposes."""
        return list(self.history)

    def validate_data(self) -> bool:
        """Ensure required fields are available before persisting the record."""
        return bool(self.record_id and self.created_by)

    def log_change(self, change: Dict[str, str]) -> None:
        """Append a change entry and update the modification timestamp."""
        self.history.append(change)
        self.updated_at = datetime.utcnow()


@dataclass
class MedicalDetails(MedicalRecord):
    """Tracks a patient's medical diagnosis and associated treatments."""

    sickness_name: str = ""
    department: str = ""
    severity: str = ""
    description: str = ""
    medications: List[str] = field(default_factory=list)
    treatments: List[str] = field(default_factory=list)
    status: str = "Pending"

    def update_description(self, new_description: str) -> bool:
        """Update the descriptive summary of the current diagnosis."""
        if not new_description:
            return False
        self.description = new_description
        self.log_change({"description": new_description})
        return True

    def update_medication(self, medication_list: List[str]) -> bool:
        """Replace the current medication plan with a new list."""
        if medication_list is None:
            return False
        self.medications = medication_list
        self.log_change({"medications": ",".join(medication_list)})
        return True

    def medication_recommendation(self) -> List[str]:
        """Suggest medications, prioritising unique items to avoid duplicates."""
        return sorted(set(self.medications))

    def track_progress(self) -> Dict[str, str]:
        """Provide a lightweight view of treatment progress."""
        return {
            "status": self.status,
            "last_updated": self.updated_at.isoformat(),
            "treatments_completed": str(len(self.history)),
        }


@dataclass
class PatientLog(MedicalRecord):
    """Captures holistic wellbeing data recorded directly from the patient."""

    personal_feeling: str = ""
    physical_condition: str = ""
    medical_condition: str = ""
    social_well_being: str = ""
    personal_needs: Dict[str, str] = field(default_factory=dict)
    feedback: List[str] = field(default_factory=list)

    def update_personal_feeling(self, feeling: str) -> bool:
        if not feeling:
            return False
        self.personal_feeling = feeling
        self.log_change({"personal_feeling": feeling})
        return True

    def update_physical_condition(self, condition: str) -> bool:
        if not condition:
            return False
        self.physical_condition = condition
        self.log_change({"physical_condition": condition})
        return True

    def update_medical_condition(self, condition: str) -> bool:
        if not condition:
            return False
        self.medical_condition = condition
        self.log_change({"medical_condition": condition})
        return True

    def update_social_wellbeing(self, wellbeing: str) -> bool:
        if not wellbeing:
            return False
        self.social_well_being = wellbeing
        self.log_change({"social_well_being": wellbeing})
        return True

    def add_feedback(self, feedback: str) -> bool:
        if not feedback:
            return False
        self.feedback.append(feedback)
        self.log_change({"feedback": feedback})
        return True

    def analyze_trends(self) -> Dict[str, str]:
        """Summarise the latest wellbeing signals for dashboards."""
        return {
            "mood": self.personal_feeling,
            "last_change": self.updated_at.isoformat(),
            "feedback_count": str(len(self.feedback)),
        }


@dataclass
class VitalSigns(MedicalRecord):
    """Stores a snapshot of vital signs collected during a patient check."""

    measurement_id: str = ""
    temperature: float = 0.0
    heart_rate: int = 0
    blood_pressure_systolic: int = 0
    blood_pressure_diastolic: int = 0
    respiratory_rate: int = 0
    oxygen_saturation: float = 0.0
    measured_at: datetime = field(default_factory=datetime.utcnow)

    def record_vitals(self, vitals_data: Dict[str, float]) -> bool:
        if not vitals_data:
            return False

        # Update each known vital sign if present in the payload.
        for field_name in (
            "temperature",
            "heart_rate",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "respiratory_rate",
            "oxygen_saturation",
        ):
            if field_name in vitals_data:
                setattr(self, field_name, vitals_data[field_name])
        self.measured_at = datetime.utcnow()
        self.log_change({"measurement": self.measured_at.isoformat()})
        return True

    def detect_anomalies(self) -> List[str]:
        """Evaluate simple thresholds to flag potential anomalies."""
        alerts: List[str] = []
        if self.temperature > 38.0:
            alerts.append("High temperature")
        if self.oxygen_saturation < 92.0:
            alerts.append("Low oxygen saturation")
        if self.heart_rate > 120 or self.heart_rate < 50:
            alerts.append("Abnormal heart rate")
        return alerts

    def generate_trend_report(self, days: int) -> Dict[str, str]:
        """Return a minimal summary, ready for further analytics."""
        return {
            "window_days": str(days),
            "last_reading": self.measured_at.isoformat(),
            "anomalies": ", ".join(self.detect_anomalies()) or "None",
        }
