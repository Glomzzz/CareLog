from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from colorama import Fore, Style

from app.alerts import Alert, NotificationService
from app.assignment import PatientAssignment
from app.medical import MedicalDetails, VitalSigns
from app.note import Note
from app.schedule import Schedule, Task
from app.user import User
from app.food import FoodToDeliver
from app.datastore import DataStore


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
        # Maintain the same method name for backwards compatibility with tests
        return DataStore.load_all()

    def _save_data(self, data: Dict[str, List[Dict[str, str]]]) -> None:
        DataStore.save_all(data)

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

    def view_schedules(self) -> List[Schedule]:
        """View all schedules assigned to this care staff member."""
        return list(self.work_schedule)

    def manage_tasks(self, task_id: str, action: str) -> bool:
        """Manage tasks by updating status or reassigning."""
        for task in self.tasks:
            if task.task_id == task_id:
                if action == "complete":
                    return task.mark_complete()
                elif action == "escalate":
                    return task.escalate_task()
                elif action.startswith("update:"):
                    status = action.split(":", 1)[1]
                    return task.update_progress(status)
        return False

    def view_assigned_patients(self) -> List[str]:
        """Return list of patient IDs assigned to this staff member."""
        return list(self.assigned_patients)

    def send_notification(self, recipient_id: str, message: str, priority: str = "normal") -> bool:
        """Send a notification through the notification service."""
        if not self.notification_service:
            return False
        # Create a mock user for notification
        from app.user import User
        recipient = User(user_id=recipient_id, name="Recipient", email=f"{recipient_id}@carelog.local", 
                        password="", role="staff")
        return self.notification_service.send_immediate_alert(recipient, message)

    def handle_alert(self, alert_id: str, action: str = "acknowledge") -> bool:
        """Handle an alert by acknowledging or resolving it."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                if action == "acknowledge":
                    return alert.acknowledge_alert(self)
                elif action == "resolve":
                    return alert.resolve_alert(self)
        return False

    def assign_patient(self, patient_id: str) -> bool:
        """Assign a patient to this care staff member."""
        if patient_id not in self.assigned_patients:
            self.assigned_patients.append(patient_id)
            assignment = PatientAssignment(
                assignment_id=f"assign-{patient_id}-{self.staff_id}",
                assigned_date=datetime.now().date(),
                assignment_type="primary",
                notes=f"Assigned to {self.name}",
            )
            assignment.assign_patient(patient_id, self.staff_id)
            self.assignments.append(assignment)
            return True
        return False

    def unassign_patient(self, patient_id: str) -> bool:
        """Remove a patient from this care staff member's assignment."""
        if patient_id in self.assigned_patients:
            self.assigned_patients.remove(patient_id)
            for assignment in self.assignments:
                if assignment.patient_id == patient_id:
                    assignment.end_assignment(patient_id)
            return True
        return False

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

    # -----------------------------
    # Serialization helpers
    # -----------------------------
    def to_dict(self) -> Dict[str, str]:
        return {
            "carestaffID": self.staff_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "specialization": self.specialization,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "CareStaff":
        return cls(
            name=data.get("name", ""),
            carestaff_id=data.get("carestaffID", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            department=data.get("department", ""),
            specialization=data.get("specialization", ""),
        )


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
            created_at=datetime.now(),
            updated_at=datetime.now(),
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

    def manage_appointments(self, appointment_id: str, action: str) -> bool:
        """Manage appointments: approve, reschedule, cancel."""
        if appointment_id in self.appointment_list:
            if action == "approve":
                return True
            elif action == "cancel":
                self.appointment_list.remove(appointment_id)
                return True
        return False

    def view_medical_records(self, patient_id: str) -> Dict[str, Any]:
        """View medical records for a specific patient."""
        record = self.patient_records.get(patient_id)
        if record:
            return record.to_dict()
        return {}

    def generate_treatment_report(self, patient_id: str) -> Dict[str, str]:
        """Generate a treatment report for a patient."""
        record = self.patient_records.get(patient_id)
        if not record:
            return {"error": "No record found"}
        return {
            "patient_id": patient_id,
            "doctor": self.name,
            "diagnosis": record.sickness_name,
            "medications": ", ".join(record.medications) if record.medications else "None",
            "status": record.status,
            "last_updated": record.updated_at.isoformat(),
        }

    def review_patient_history(self, patient_id: str) -> List[str]:
        """Review patient medical history from records."""
        record = self.patient_records.get(patient_id)
        if record:
            # Extract change descriptions from history
            return [
                change.get("description", "") or 
                change.get("medications", "") or 
                str(change) 
                for change in record.history
            ]
        return []

    def add_appointment(self, appointment_id: str) -> bool:
        """Add an appointment to the doctor's schedule."""
        if appointment_id not in self.appointment_list:
            self.appointment_list.append(appointment_id)
            return True
        return False

    def to_dict(self) -> Dict[str, str]:
        base = super().to_dict()
        base.update(
            {
                "role": "doctor",
                "licenseNumber": self.license_number,
                "certifications": list(self.certifications),
                "workToDo": self.work_to_do,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Doctor":
        return cls(
            name=data.get("name", ""),
            carestaff_id=data.get("carestaffID", ""),
            license_number=data.get("licenseNumber", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            certifications=list(data.get("certifications", [])),
            work_to_do=data.get("workToDo", ""),
            department=data.get("department", ""),
            specialization=data.get("specialization", ""),
        )


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
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=self.staff_id,
        )
        record.record_vitals(vitals)
        self.vital_signs[patient_id] = record
        return True

    def coordinate_care(self, patient_id: str, care_plan: Dict[str, str]) -> bool:
        assignment = PatientAssignment(
            assignment_id=f"assign-{patient_id}-{self.staff_id}",
            assigned_date=datetime.now().date(),
            assignment_type=care_plan.get("type", "nursing"),
            notes=care_plan.get("notes", ""),
        )
        return assignment.assign_patient(patient_id, self.staff_id)

    def manage_food_deliveries(self, delivery_id: str, action: str) -> bool:
        """Manage food deliveries: mark delivered, cancel, verify."""
        for delivery in self.food_deliveries:
            if delivery.delivery_id == delivery_id:
                if action == "delivered":
                    return delivery.update_delivery_status("delivered")
                elif action == "cancel":
                    return delivery.update_delivery_status("cancelled")
                elif action == "verify":
                    return True
        return False

    def create_food_delivery(self, patient_id: str, food_items: str, room_number: int, scheduled_time: datetime) -> FoodToDeliver:
        """Create a new food delivery for a patient."""
        delivery = FoodToDeliver(
            delivery_id=f"del-{patient_id}-{len(self.food_deliveries) + 1}",
            food_items=food_items,
            room_number=room_number,
            scheduled_time=scheduled_time,
        )
        self.food_deliveries.append(delivery)
        return delivery

    def view_pending_tasks(self) -> List[Task]:
        """View all pending tasks assigned to this nurse."""
        return [task for task in self.tasks if task.status in ["pending", "in-progress"]]

    def mark_medication_administered(self, patient_id: str, medication: Dict[str, str]) -> bool:
        """Mark that a medication has been administered to a patient."""
        if self.administer_medication(patient_id, medication):
            # Create a task record
            task = Task(
                task_id=f"med-{patient_id}-{datetime.now().timestamp()}",
                title=f"Administer {medication.get('name', 'medication')}",
                description=f"Administered to patient {patient_id}",
                priority="normal",
                status="completed",
                due_date=datetime.now(),
            )
            task.completed_at = datetime.now()
            self.tasks.append(task)
            return True
        return False

    def get_patient_vitals(self, patient_id: str) -> Dict[str, Any]:
        """Retrieve vital signs for a specific patient."""
        vitals = self.vital_signs.get(patient_id)
        if vitals:
            return vitals.to_dict()
        return {}

    def to_dict(self) -> Dict[str, str]:
        base = super().to_dict()
        base.update(
            {
                "role": "nurse",
                "licenseNumber": self.license_number,
                "qualifications": list(self.qualifications),
                "workToDo": self.work_to_do,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Nurse":
        return cls(
            name=data.get("name", ""),
            carestaff_id=data.get("carestaffID", ""),
            license_number=data.get("licenseNumber", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            qualifications=list(data.get("qualifications", [])),
            work_to_do=data.get("workToDo", ""),
            department=data.get("department", ""),
            specialization=data.get("specialization", ""),
        )

