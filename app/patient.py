from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from app.medical import MedicalDetails, MedicalRecord, PatientLog, VitalSigns
from app.user import User

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from app.schedule import Appointment, Schedule


@dataclass
class Diet:
    """Represents a patient's meal plan preferences and restrictions."""

    diet_id: str
    food_to_serve: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    food_preferences: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    nutritional_goals: str = ""

    def check_allergies(self, food_item: str) -> bool:
        """Return True when the food item is safe for the patient."""
        return food_item.lower() not in {a.lower() for a in self.allergies}

    def update_food_to_serve(self, food_list: List[str]) -> bool:
        if food_list is None:
            return False
        self.food_to_serve = food_list
        return True

    def update_allergies(self, allergy_list: List[str]) -> bool:
        if allergy_list is None:
            return False
        self.allergies = allergy_list
        return True

    def update_food_preferences(self, preferences: List[str]) -> bool:
        if preferences is None:
            return False
        self.food_preferences = preferences
        return True

    def generate_nutrition_report(self) -> Dict[str, Any]:
        """Return a lightweight report for nutritionists."""
        return {
            "diet_id": self.diet_id,
            "goals": self.nutritional_goals,
            "restrictions": self.restrictions,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dietID": self.diet_id,
            "foodToServe": list(self.food_to_serve),
            "allergies": list(self.allergies),
            "foodPreferences": list(self.food_preferences),
            "restrictions": list(self.restrictions),
            "nutritionalGoals": self.nutritional_goals,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Diet":
        return cls(
            diet_id=data.get("dietID", ""),
            food_to_serve=list(data.get("foodToServe", [])),
            allergies=list(data.get("allergies", [])),
            food_preferences=list(data.get("foodPreferences", [])),
            restrictions=list(data.get("restrictions", [])),
            nutritional_goals=data.get("nutritionalGoals", ""),
        )


@dataclass
class Feedback:
    """Stores patient feedback and tracks its follow-up lifecycle."""

    feedback_id: str
    rating: int
    comments: str
    category: str = "general"
    submitted_at: datetime = field(default_factory=datetime.now)
    status: str = "open"
    actions_taken: List[str] = field(default_factory=list)

    def submit_feedback(self, submitter: User, feedback_data: Dict[str, Any]) -> bool:
        if not feedback_data:
            return False
        # Capture actions for auditing purposes.
        self.actions_taken.append(f"Submitted by {submitter.user_id}")
        self.comments = feedback_data.get("comments", self.comments)
        self.rating = feedback_data.get("rating", self.rating)
        self.category = feedback_data.get("category", self.category)
        return True

    def analyze_sentiment(self) -> str:
        """Very lightweight sentiment estimation based on the rating."""
        if self.rating >= 4:
            return "positive"
        if self.rating <= 2:
            return "negative"
        return "neutral"

    def track_resolution(self) -> bool:
        """Consider the feedback resolved once an action is recorded."""
        return bool(self.actions_taken)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedbackID": self.feedback_id,
            "rating": self.rating,
            "comments": self.comments,
            "category": self.category,
            "submittedAt": self.submitted_at.isoformat(),
            "status": self.status,
            "actionsTaken": list(self.actions_taken),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Feedback":
        return cls(
            feedback_id=data.get("feedbackID", ""),
            rating=int(data.get("rating", 0)),
            comments=data.get("comments", ""),
            category=data.get("category", "general"),
            submitted_at=datetime.fromisoformat(data.get("submittedAt")) if data.get("submittedAt") else datetime.now(),
            status=data.get("status", "open"),
            actions_taken=list(data.get("actionsTaken", [])),
        )


@dataclass
class Patient(User):
    """Represents a patient and aggregates their care-related artefacts."""

    patient_id: str = ""
    emergency_contact: str = ""
    insurance_info: str = ""
    address: str = ""
    date_admitted: Optional[datetime] = None
    date_discharged: Optional[datetime] = None
    status: str = "admitted"
    high_risk: bool = False
    primary_diagnosis: str = ""
    diet: Optional[Diet] = None
    medical_records: List[MedicalRecord] = field(default_factory=list)
    schedules: List["Schedule"] = field(default_factory=list)
    appointments: List["Appointment"] = field(default_factory=list)
    feedback_entries: List[Feedback] = field(default_factory=list)

    def __post_init__(self) -> None:
        # The patient identifier mirrors the user identifier for consistency.
        if not self.patient_id:
            self.patient_id = self.user_id

    def give_feedback(self, rating: int, comments: str) -> bool:
        if rating < 1 or rating > 5:
            return False
        feedback = Feedback(
            feedback_id=f"fb-{len(self.feedback_entries) + 1}",
            rating=rating,
            comments=comments,
        )
        self.feedback_entries.append(feedback)
        return True

    def update_personal_details(self, updates: Dict[str, Any]) -> bool:
        """Update mutable personal details such as address."""
        allowed = {"address", "emergency_contact", "insurance_info", "status", "primary_diagnosis", "high_risk"}
        updated = False
        for key, value in updates.items():
            if key in allowed:
                setattr(self, key, value)
                updated = True
        return updated

    def view_medical_record(self) -> Optional[MedicalRecord]:
        """Return the latest medical record if available."""
        return self.medical_records[-1] if self.medical_records else None

    def request_appointment(self, preferences: Dict[str, Any]) -> "Appointment":
        from app.schedule import Appointment  # Local import to avoid cycles.

        appointment = Appointment.create_from_preferences(self, preferences)
        self.appointments.append(appointment)
        return appointment

    def view_schedule(self) -> List["Schedule"]:
        """Expose scheduled items for downstream consumers."""
        return list(self.schedules)

    def add_medical_record(self, record: MedicalRecord) -> None:
        self.medical_records.append(record)

    def add_schedule(self, schedule: "Schedule") -> None:
        self.schedules.append(schedule)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise patient data while keeping backward compatibility."""
        return {
            "patientID": self.patient_id,
            "name": self.name,
            "disease": self.primary_diagnosis,
            "high_risk": self.high_risk,
            "emergencyContact": self.emergency_contact,
            "insuranceInfo": self.insurance_info,
            "address": self.address,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Patient":
        # Map incoming dict to User base + Patient fields
        return cls(
            user_id=data.get("patientID", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=data.get("role", "patient"),
            emergency_contact=data.get("emergencyContact", ""),
            insurance_info=data.get("insuranceInfo", ""),
            address=data.get("address", ""),
            primary_diagnosis=data.get("disease", ""),
            status=data.get("status", "admitted"),
            high_risk=bool(data.get("high_risk", False)),
        )


@dataclass
class FamilyMember(User):
    """Represents a relative associated with one or more patients."""

    relationship: str = ""
    contact_info: str = ""
    is_emergency_contact: bool = False
    linked_patients: List[Patient] = field(default_factory=list)

    def view_patient_status(self, patient_id: str) -> Dict[str, Any]:
        for patient in self.linked_patients:
            if patient.patient_id == patient_id:
                return {
                    "status": patient.status,
                    "diagnosis": patient.primary_diagnosis,
                    "high_risk": patient.high_risk,
                }
        return {}

    def provide_feedback(self, patient_id: str, feedback: Dict[str, Any]) -> bool:
        for patient in self.linked_patients:
            if patient.patient_id == patient_id:
                return patient.give_feedback(
                    rating=feedback.get("rating", 3),
                    comments=feedback.get("comments", ""),
                )
        return False

    def update_patient_preferences(self, patient_id: str, preferences: Dict[str, Any]) -> bool:
        for patient in self.linked_patients:
            if patient.patient_id == patient_id and patient.diet:
                patient.diet.update_food_preferences(preferences.get("food_preferences", []))
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userID": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "relationship": self.relationship,
            "contactInfo": self.contact_info,
            "isEmergencyContact": self.is_emergency_contact,
            "linkedPatients": [p.patient_id for p in self.linked_patients],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FamilyMember":
        return cls(
            user_id=data.get("userID", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=data.get("role", "family"),
            relationship=data.get("relationship", ""),
            contact_info=data.get("contactInfo", ""),
            is_emergency_contact=bool(data.get("isEmergencyContact", False)),
        )
