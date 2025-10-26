from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List

from colorama import Fore, Style

from app.alerts import Alert, NotificationService
from app.assignment import PatientAssignment
from app.medical import MedicalDetails, VitalSigns
from app.note import Note
from app.schedule import Schedule, Task
from app.user import User
from app.food import FoodToDeliver


class CareStaff(User):
    """Hybrid domain/service class representing a member of the care team."""

    def __init__(
        self,
        name: str,
        carestaff_id: str,
        *,
        email: str = "",
        password: str = "",
        department: str = "",
        specialization: str = "",
        notification_service: NotificationService | None = None,
    ) -> None:
        super().__init__(
            user_id=carestaff_id,
            name=name,
            email=email or f"{carestaff_id}@carelog.local",
            password=password or "",
            role="carestaff",
        )
        self.staff_id = carestaff_id
        self.department = department
        self.specialization = specialization
        self.assigned_patients: List[str] = []
        self.work_schedule: List[Schedule] = []
        self.tasks: List[Task] = []
        self.alerts: List[Alert] = []
        self.assignments: List[PatientAssignment] = []
        self.notification_service = notification_service or NotificationService(
            service_id=f"notif-{carestaff_id}",
            channels=["email", "sms"],
        )

    # ---------------------------------------------------------------------
    # Persistence helpers
    # ---------------------------------------------------------------------
    def _load_data(self) -> Dict[str, List[Dict[str, str]]]:
        with open("data/carelog.json", "r") as f:
            return json.load(f)

    def _save_data(self, data: Dict[str, List[Dict[str, str]]]) -> None:
        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    # ---------------------------------------------------------------------
    # Domain operations from the class diagram
    # ---------------------------------------------------------------------
    def update_patient_records(self, patient_id: str, updates: Dict[str, str]) -> bool:
        data = self._load_data()
        for patient in data.get("patients", []):
            if patient.get("patientID") == patient_id:
                patient.update(updates)
                self._save_data(data)
                return True
        return False

    def view_patient_alerts(self) -> List[Alert]:
        return list(self.alerts)

    def generate_reports(self, start_date: datetime, end_date: datetime) -> Dict[str, str]:
        return {
            "staff": self.name,
            "period": f"{start_date.date()} to {end_date.date()}",
            "patients_managed": str(len(self.assigned_patients)),
            "tasks_completed": str(sum(1 for t in self.tasks if t.status == "completed")),
        }

    # ---------------------------------------------------------------------
    # Existing CLI-driven operations (retained for backwards compatibility)
    # ---------------------------------------------------------------------
    def add_note(self, patient_id: str, content: str) -> None:
        data = self._load_data()
        note = Note(patient_id, self.staff_id, content)
        data.setdefault("notes", []).append(note.to_dict())
        self._save_data(data)
        print(Fore.GREEN + "Note added successfully!" + Style.RESET_ALL)

    def update_disease(self, patient_id: str, new_disease: str) -> None:
        if self.update_patient_records(patient_id, {"disease": new_disease}):
            print(Fore.GREEN + f"Disease updated for {patient_id}!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Patient not found." + Style.RESET_ALL)

    def search_patient(self, keyword: str) -> None:
        data = self._load_data()
        print(Fore.CYAN + "Search results:" + Style.RESET_ALL)
        for patient in data.get("patients", []):
            if keyword.lower() in patient.get("name", "").lower() or keyword.lower() in patient.get("patientID", "").lower():
                risk_color = Fore.YELLOW if patient.get("high_risk") else Fore.WHITE
                print(
                    risk_color
                    + f"ID: {patient.get('patientID')} | Name: {patient.get('name')} | Disease: {patient.get('disease')}"
                    + Style.RESET_ALL
                )

    def view_notes(self, patient_id: str) -> None:
        data = self._load_data()
        found = [note for note in data.get("notes", []) if note.get("patientID") == patient_id]
        if not found:
            print(Fore.RED + "No notes found for this patient." + Style.RESET_ALL)
            return

        print(Fore.CYAN + f"Notes for patient {patient_id}:" + Style.RESET_ALL)
        for note in found:
            print(f"- ({note['timestamp']}) {note['content']} (by {note['author']})")

    def add_schedule(self, task: str, date: str) -> None:
        data = self._load_data()
        schedule = Schedule(self.staff_id, task, date)
        data.setdefault("schedules", []).append(schedule.to_dict())
        self.work_schedule.append(schedule)
        self._save_data(data)
        print(Fore.GREEN + "Schedule added successfully!" + Style.RESET_ALL)

    def toggle_high_risk(self, patient_id: str) -> None:
        data = self._load_data()
        for patient in data.get("patients", []):
            if patient.get("patientID") == patient_id:
                patient["high_risk"] = not patient.get("high_risk", False)
                self._save_data(data)
                if patient["high_risk"]:
                    print(Fore.YELLOW + f"Patient {patient['name']} is now marked HIGH RISK!" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"Patient {patient['name']} is no longer high risk." + Style.RESET_ALL)
                return

        print(Fore.RED + "Patient not found." + Style.RESET_ALL)


class Doctor(CareStaff):
    """Specialised care staff capable of managing medical treatment plans."""

    def __init__(
        self,
        name: str,
        carestaff_id: str,
        license_number: str,
        *,
        certifications: List[str] | None = None,
        appointment_list: List[str] | None = None,
        work_to_do: str = "",
        **kwargs,
    ) -> None:
        super().__init__(name, carestaff_id, **kwargs)
        self.license_number = license_number
        self.certifications = certifications or []
        self.appointment_list = appointment_list or []
        self.work_to_do = work_to_do
        self.patient_records: Dict[str, MedicalDetails] = {}

    def update_medical_details(self, patient_id: str, medical_info: Dict[str, str]) -> bool:
        record = self.patient_records.get(patient_id) or MedicalDetails(
            record_id=f"med-{patient_id}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=self.staff_id,
            sickness_name=medical_info.get("sickness_name", ""),
            department=medical_info.get("department", self.department),
        )
        if "description" in medical_info:
            record.update_description(medical_info["description"])
        if "medications" in medical_info:
            record.update_medication(medical_info["medications"])
        self.patient_records[patient_id] = record
        return True

    def prescribe_medication(self, patient_id: str, medication: Dict[str, str]) -> bool:
        record = self.patient_records.get(patient_id)
        if not record:
            return False
        meds = list(record.medications)
        meds.append(medication.get("name", ""))
        record.update_medication(meds)
        return True

    def approve_treatment_plans(self, patient_id: str, plan: Dict[str, str]) -> bool:
        record = self.patient_records.get(patient_id)
        if not record:
            return False
        record.status = plan.get("status", "approved")
        return True

    def escalate_to_specialist(self, patient_id: str, specialist_type: str) -> bool:
        alert = Alert(
            alert_id=f"alert-{patient_id}-{len(self.alerts) + 1}",
            type="escalation",
            severity="high",
            message=f"Escalate {patient_id} to {specialist_type}",
        )
        self.alerts.append(alert)
        return True


class Nurse(CareStaff):
    """Care staff member focused on day-to-day patient support."""

    def __init__(
        self,
        name: str,
        carestaff_id: str,
        license_number: str,
        *,
        qualifications: List[str] | None = None,
        food_deliveries: List[FoodToDeliver] | None = None,
        work_to_do: str = "",
        **kwargs,
    ) -> None:
        super().__init__(name, carestaff_id, **kwargs)
        self.license_number = license_number
        self.qualifications = qualifications or []
        self.food_deliveries = food_deliveries or []
        self.work_to_do = work_to_do
        self.vital_signs: Dict[str, VitalSigns] = {}

    def administer_medication(self, patient_id: str, medication: Dict[str, str]) -> bool:
        return bool(patient_id and medication)

    def update_vital_signs(self, patient_id: str, vitals: Dict[str, float]) -> bool:
        record = self.vital_signs.get(patient_id) or VitalSigns(
            record_id=f"vitals-{patient_id}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=self.staff_id,
        )
        record.record_vitals(vitals)
        self.vital_signs[patient_id] = record
        return True

    def coordinate_care(self, patient_id: str, care_plan: Dict[str, str]) -> bool:
        assignment = PatientAssignment(
            assignment_id=f"assign-{patient_id}-{self.staff_id}",
            assigned_date=datetime.utcnow().date(),
            assignment_type=care_plan.get("type", "nursing"),
            notes=care_plan.get("notes", ""),
        )
        return assignment.assign_patient(patient_id, self.staff_id)

