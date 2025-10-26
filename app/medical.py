from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


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
        now = datetime.now()
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
        self.updated_at = datetime.now()

    # -----------------------------
    # Serialization helpers
    # -----------------------------
    def to_base_dict(self) -> Dict[str, Any]:
        return {
            "recordID": self.record_id,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by,
            "history": list(self.history),
        }


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
        from app.datastore import DataStore
        if not new_description:
            return False
        self.description = new_description
        self.log_change({"description": new_description})
        DataStore.upsert("medical_details", "recordID", self.to_dict())
        return True

    def update_medication(self, medication_list: List[str]) -> bool:
        """Replace the current medication plan with a new list."""
        from app.datastore import DataStore
        if medication_list is None:
            return False
        self.medications = medication_list
        self.log_change({"medications": ",".join(medication_list)})
        DataStore.upsert("medical_details", "recordID", self.to_dict())
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

    def to_dict(self) -> Dict[str, Any]:
        base = self.to_base_dict()
        base.update(
            {
                "type": "MedicalDetails",
                "sicknessName": self.sickness_name,
                "department": self.department,
                "severity": self.severity,
                "description": self.description,
                "medications": list(self.medications),
                "treatments": list(self.treatments),
                "status": self.status,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MedicalDetails":
        return cls(
            record_id=data.get("recordID", ""),
            created_at=datetime.fromisoformat(data.get("createdAt")) if data.get("createdAt") else datetime.now(),
            updated_at=datetime.fromisoformat(data.get("updatedAt")) if data.get("updatedAt") else datetime.now(),
            created_by=data.get("createdBy", ""),
            history=list(data.get("history", [])),
            sickness_name=data.get("sicknessName", ""),
            department=data.get("department", ""),
            severity=data.get("severity", ""),
            description=data.get("description", ""),
            medications=list(data.get("medications", [])),
            treatments=list(data.get("treatments", [])),
            status=data.get("status", "Pending"),
        )


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
        from app.datastore import DataStore
        if not feeling:
            return False
        self.personal_feeling = feeling
        self.log_change({"personal_feeling": feeling})
        DataStore.upsert("patient_logs", "recordID", self.to_dict())
        return True

    def update_physical_condition(self, condition: str) -> bool:
        from app.datastore import DataStore
        if not condition:
            return False
        self.physical_condition = condition
        self.log_change({"physical_condition": condition})
        DataStore.upsert("patient_logs", "recordID", self.to_dict())
        return True

    def update_medical_condition(self, condition: str) -> bool:
        from app.datastore import DataStore
        if not condition:
            return False
        self.medical_condition = condition
        self.log_change({"medical_condition": condition})
        DataStore.upsert("patient_logs", "recordID", self.to_dict())
        return True

    def update_social_wellbeing(self, wellbeing: str) -> bool:
        from app.datastore import DataStore
        if not wellbeing:
            return False
        self.social_well_being = wellbeing
        self.log_change({"social_well_being": wellbeing})
        DataStore.upsert("patient_logs", "recordID", self.to_dict())
        return True

    def add_feedback(self, feedback: str) -> bool:
        from app.datastore import DataStore
        if not feedback:
            return False
        self.feedback.append(feedback)
        self.log_change({"feedback": feedback})
        DataStore.upsert("patient_logs", "recordID", self.to_dict())
        return True

    def analyze_trends(self) -> Dict[str, str]:
        """Summarise the latest wellbeing signals for dashboards."""
        return {
            "mood": self.personal_feeling,
            "last_change": self.updated_at.isoformat(),
            "feedback_count": str(len(self.feedback)),
        }

    def to_dict(self) -> Dict[str, Any]:
        base = self.to_base_dict()
        base.update(
            {
                "type": "PatientLog",
                "personalFeeling": self.personal_feeling,
                "physicalCondition": self.physical_condition,
                "medicalCondition": self.medical_condition,
                "socialWellBeing": self.social_well_being,
                "personalNeeds": dict(self.personal_needs),
                "feedback": list(self.feedback),
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientLog":
        return cls(
            record_id=data.get("recordID", ""),
            created_at=datetime.fromisoformat(data.get("createdAt")) if data.get("createdAt") else datetime.now(),
            updated_at=datetime.fromisoformat(data.get("updatedAt")) if data.get("updatedAt") else datetime.now(),
            created_by=data.get("createdBy", ""),
            history=list(data.get("history", [])),
            personal_feeling=data.get("personalFeeling", ""),
            physical_condition=data.get("physicalCondition", ""),
            medical_condition=data.get("medicalCondition", ""),
            social_well_being=data.get("socialWellBeing", ""),
            personal_needs=dict(data.get("personalNeeds", {})),
            feedback=list(data.get("feedback", [])),
        )


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
    measured_at: datetime = field(default_factory=datetime.now)

    def record_vitals(self, vitals_data: Dict[str, float]) -> bool:
        from app.datastore import DataStore
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
        self.measured_at = datetime.now()
        self.log_change({"measurement": self.measured_at.isoformat()})
        DataStore.upsert("vital_signs", "recordID", self.to_dict())
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

    def to_dict(self) -> Dict[str, Any]:
        base = self.to_base_dict()
        base.update(
            {
                "type": "VitalSigns",
                "measurementID": self.measurement_id,
                "temperature": self.temperature,
                "heartRate": self.heart_rate,
                "bloodPressureSystolic": self.blood_pressure_systolic,
                "bloodPressureDiastolic": self.blood_pressure_diastolic,
                "respiratoryRate": self.respiratory_rate,
                "oxygenSaturation": self.oxygen_saturation,
                "measuredAt": self.measured_at.isoformat(),
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VitalSigns":
        return cls(
            record_id=data.get("recordID", ""),
            created_at=datetime.fromisoformat(data.get("createdAt")) if data.get("createdAt") else datetime.now(),
            updated_at=datetime.fromisoformat(data.get("updatedAt")) if data.get("updatedAt") else datetime.now(),
            created_by=data.get("createdBy", ""),
            history=list(data.get("history", [])),
            measurement_id=data.get("measurementID", ""),
            temperature=float(data.get("temperature", 0.0)),
            heart_rate=int(data.get("heartRate", 0)),
            blood_pressure_systolic=int(data.get("bloodPressureSystolic", 0)),
            blood_pressure_diastolic=int(data.get("bloodPressureDiastolic", 0)),
            respiratory_rate=int(data.get("respiratoryRate", 0)),
            oxygen_saturation=float(data.get("oxygenSaturation", 0.0)),
            measured_at=datetime.fromisoformat(data.get("measuredAt")) if data.get("measuredAt") else datetime.now(),
        )
