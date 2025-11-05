"""Comprehensive unit tests for CareStaff, Doctor, and Nurse classes."""
from datetime import datetime, timedelta

import pytest

from app.model.alerts import Alert, NotificationService
from app.model.carestaff import CareStaff, Doctor, Nurse
from app.model.food import FoodToDeliver
from app.model.medical import MedicalDetails, VitalSigns
from app.model.schedule import Schedule, Task
from app.model.assignment import PatientAssignment


@pytest.fixture
def mock_datastore(monkeypatch):
    """Mock datastore for testing."""
    store = {
        "patients": [
            {"id": "p1", "name": "Alice", "disease": "Flu", "high_risk": False},
            {"id": "p2", "name": "Bob", "disease": "Cold", "high_risk": True},
        ],
        "notes": [],
        "schedules": [],
        "carestaffs": [],
    }

    monkeypatch.setattr(CareStaff, "_load_data", lambda self: store)
    monkeypatch.setattr(CareStaff, "_save_data", lambda self, data: store.update(data))
    
    
    return store


class TestCareStaff:
    """Test base CareStaff functionality."""

    def test_carestaff_initialization(self):
        staff = CareStaff("Jane Doe", "cs001", email="jane@hospital.com", department="General")
        assert staff.name == "Jane Doe"
        assert staff.staff_id == "cs001"
        assert staff.department == "General"
        assert staff.email == "jane@hospital.com"
        assert len(staff.assigned_patients) == 0
        assert len(staff.tasks) == 0

    def test_view_schedules(self):
        staff = CareStaff("John", "cs002")
        schedule1 = Schedule("cs002", "Morning Rounds", "2025-01-01")
        schedule2 = Schedule("cs002", "Evening Check", "2025-01-01")
        staff.work_schedule = [schedule1, schedule2]
        
        schedules = staff.view_schedules()
        assert len(schedules) == 2
        assert schedules[0].task == "Morning Rounds"

    def test_manage_tasks_complete(self):
        staff = CareStaff("Emma", "cs003")
        task = Task(
            task_id="t1",
            title="Check Patient",
            description="Morning check",
            priority="high",
            status="pending",
            due_date=datetime.now() + timedelta(hours=2),
        )
        staff.tasks.append(task)
        
        result = staff.manage_tasks("t1", "complete")
        assert result is True
        assert task.status == "completed"
        assert task.completed_at is not None

    def test_manage_tasks_escalate(self):
        staff = CareStaff("Oliver", "cs004")
        task = Task(
            task_id="t2",
            title="Review Labs",
            description="Lab results",
            priority="normal",
            status="pending",
            due_date=datetime.now(),
        )
        staff.tasks.append(task)
        
        result = staff.manage_tasks("t2", "escalate")
        assert result is True
        assert task.priority == "high"

    def test_manage_tasks_update_status(self):
        staff = CareStaff("Sophia", "cs005")
        task = Task(
            task_id="t3",
            title="Update Records",
            description="Patient records",
            priority="normal",
            status="pending",
            due_date=datetime.now(),
        )
        staff.tasks.append(task)
        
        result = staff.manage_tasks("t3", "update:in-progress")
        assert result is True
        assert task.status == "in-progress"

    def test_view_assigned_patients(self):
        staff = CareStaff("Liam", "cs006")
        staff.assigned_patients = ["p1", "p2", "p3"]
        
        patients = staff.view_assigned_patients()
        assert len(patients) == 3
        assert "p1" in patients

    def test_send_notification(self):
        notifier = NotificationService(service_id="notif1", channels=["email"])
        staff = CareStaff("Ava", "cs007", notification_service=notifier)
        
        result = staff.send_notification("p1", "Appointment reminder", "high")
        assert result is True

    def test_handle_alert_acknowledge(self):
        staff = CareStaff("Noah", "cs008")
        alert = Alert(
            alert_id="a1",
            type="system",
            severity="medium",
            message="System check required",
        )
        staff.alerts.append(alert)
        
        result = staff.handle_alert("a1", "acknowledge")
        assert result is True
        assert alert.acknowledged_at is not None

    def test_handle_alert_resolve(self):
        staff = CareStaff("Isabella", "cs009")
        alert = Alert(
            alert_id="a2",
            type="patient",
            severity="high",
            message="Patient needs attention",
        )
        staff.alerts.append(alert)
        
        result = staff.handle_alert("a2", "resolve")
        assert result is True
        assert alert.resolved_at is not None

    def test_assign_patient(self):
        staff = CareStaff("Mia", "cs010")
        
        result = staff.assign_patient("p1")
        assert result is True
        assert "p1" in staff.assigned_patients
        assert len(staff.assignments) == 1
        
        # Test duplicate assignment
        result = staff.assign_patient("p1")
        assert result is False

    def test_unassign_patient(self):
        staff = CareStaff("Lucas", "cs011")
        staff.assigned_patients.append("p1")
        assignment = PatientAssignment(
            assignment_id="assign1",
            assigned_date=datetime.now().date(),
            assignment_type="primary",
        )
        assignment.assign_patient("p1", "cs011")
        staff.assignments.append(assignment)
        
        result = staff.unassign_patient("p1")
        assert result is True
        assert "p1" not in staff.assigned_patients

    def test_update_patient_records(self, mock_datastore):
        staff = CareStaff("Ethan", "cs012")
        
        result = staff.update_patient_records("p1", {"disease": "Pneumonia"})
        assert result is True
        assert mock_datastore["patients"][0]["disease"] == "Pneumonia"

    def test_view_patient_alerts(self):
        staff = CareStaff("Charlotte", "cs013")
        alert1 = Alert("a1", "system", "low", "Test 1")
        alert2 = Alert("a2", "patient", "high", "Test 2")
        staff.alerts = [alert1, alert2]
        
        alerts = staff.view_patient_alerts()
        assert len(alerts) == 2

    def test_generate_reports(self):
        staff = CareStaff("Harper", "cs014")
        staff.assigned_patients = ["p1", "p2"]
        task1 = Task("t1", "Task 1", "Desc", "normal", "completed", datetime.now())
        task2 = Task("t2", "Task 2", "Desc", "normal", "pending", datetime.now())
        staff.tasks = [task1, task2]
        
        report = staff.generate_reports(datetime(2025, 1, 1), datetime(2025, 1, 31))
        assert report["patients_managed"] == "2"
        assert report["tasks_completed"] == "1"

    def test_serialization(self):
        staff = CareStaff("Amelia", "cs015", email="amelia@hospital.com", department="ICU")
        data = staff.to_dict()
        
        assert data["id"] == "cs015"
        assert data["name"] == "Amelia"
        assert data["department"] == "ICU"
        
        restored = CareStaff.from_dict(data)
        assert restored.staff_id == "cs015"
        assert restored.name == "Amelia"


class TestDoctor:
    """Test Doctor-specific functionality."""

    def test_doctor_initialization(self):
        doctor = Doctor(
            "Dr. Smith",
            "doc001",
            license_number="LIC123",
            department="Cardiology",
            certifications=["Board Certified", "Fellowship"],
        )
        assert doctor.name == "Dr. Smith"
        assert doctor.license_number == "LIC123"
        assert len(doctor.certifications) == 2
        assert len(doctor.patient_records) == 0

    def test_update_medical_details_new_patient(self):
        doctor = Doctor("Dr. Jones", "doc002", license_number="LIC456")
        
        result = doctor.update_medical_details(
            "p1",
            {
                "sickness_name": "Hypertension",
                "description": "Stage 1 hypertension",
                "medications": ["Lisinopril"],
            },
        )
        assert result is True
        assert "p1" in doctor.patient_records
        assert doctor.patient_records["p1"].sickness_name == "Hypertension"

    def test_update_medical_details_existing_patient(self):
        doctor = Doctor("Dr. Brown", "doc003", license_number="LIC789")
        # Create initial record
        doctor.update_medical_details("p1", {"sickness_name": "Diabetes"})
        
        # Update existing
        result = doctor.update_medical_details(
            "p1",
            {"description": "Type 2 diabetes, well controlled"},
        )
        assert result is True
        assert "diabetes" in doctor.patient_records["p1"].description.lower()

    def test_prescribe_medication(self):
        doctor = Doctor("Dr. Wilson", "doc004", license_number="LIC101")
        doctor.update_medical_details("p1", {"sickness_name": "Infection"})
        
        result = doctor.prescribe_medication("p1", {"name": "Amoxicillin"})
        assert result is True
        assert "Amoxicillin" in doctor.patient_records["p1"].medications

    def test_prescribe_medication_no_record(self):
        doctor = Doctor("Dr. Davis", "doc005", license_number="LIC202")
        
        result = doctor.prescribe_medication("p999", {"name": "Aspirin"})
        assert result is False

    def test_approve_treatment_plans(self):
        doctor = Doctor("Dr. Miller", "doc006", license_number="LIC303")
        doctor.update_medical_details("p1", {"sickness_name": "Cancer"})
        
        result = doctor.approve_treatment_plans("p1", {"status": "approved"})
        assert result is True
        assert doctor.patient_records["p1"].status == "approved"

    def test_escalate_to_specialist(self):
        doctor = Doctor("Dr. Garcia", "doc007", license_number="LIC404")
        
        result = doctor.escalate_to_specialist("p1", "Neurology")
        assert result is True
        assert len(doctor.alerts) == 1
        assert doctor.alerts[0].type == "escalation"
        assert doctor.alerts[0].severity == "high"

    def test_manage_appointments_approve(self):
        doctor = Doctor("Dr. Martinez", "doc008", license_number="LIC505")
        doctor.appointment_list.append("appt001")
        
        result = doctor.manage_appointments("appt001", "approve")
        assert result is True

    def test_manage_appointments_cancel(self):
        doctor = Doctor("Dr. Rodriguez", "doc009", license_number="LIC606")
        doctor.appointment_list.append("appt002")
        
        result = doctor.manage_appointments("appt002", "cancel")
        assert result is True
        assert "appt002" not in doctor.appointment_list

    def test_view_medical_records(self):
        doctor = Doctor("Dr. Lee", "doc010", license_number="LIC707")
        doctor.update_medical_details("p1", {"sickness_name": "Asthma"})
        
        records = doctor.view_medical_records("p1")
        assert "sicknessName" in records  # Note: serialized key is camelCase
        assert records["sicknessName"] == "Asthma"

    def test_view_medical_records_not_found(self):
        doctor = Doctor("Dr. White", "doc011", license_number="LIC808")
        
        records = doctor.view_medical_records("p999")
        assert records == {}

    def test_generate_treatment_report(self):
        doctor = Doctor("Dr. Harris", "doc012", license_number="LIC909")
        doctor.update_medical_details(
            "p1",
            {
                "sickness_name": "Pneumonia",
                "medications": ["Azithromycin", "Ibuprofen"],
            },
        )
        
        report = doctor.generate_treatment_report("p1")
        assert report["patient_id"] == "p1"
        assert report["diagnosis"] == "Pneumonia"
        assert "Azithromycin" in report["medications"]

    def test_review_patient_history(self):
        doctor = Doctor("Dr. Clark", "doc013", license_number="LIC010")
        doctor.update_medical_details("p1", {"sickness_name": "Flu"})
        record = doctor.patient_records["p1"]
        record.log_change({"description": "Initial diagnosis"})
        record.log_change({"description": "Symptoms improved"})
        
        history = doctor.review_patient_history("p1")
        assert len(history) == 2
        assert "Initial diagnosis" in history[0]

    def test_add_appointment(self):
        doctor = Doctor("Dr. Lewis", "doc014", license_number="LIC111")
        
        result = doctor.add_appointment("appt003")
        assert result is True
        assert "appt003" in doctor.appointment_list
        
        # Test duplicate
        result = doctor.add_appointment("appt003")
        assert result is False

    def test_doctor_serialization(self):
        doctor = Doctor(
            "Dr. Walker",
            "doc015",
            license_number="LIC212",
            certifications=["Cardiology"],
            work_to_do="Patient consultations",
        )
        data = doctor.to_dict()
        
        assert data["role"] == "doctor"
        assert data["licenseNumber"] == "LIC212"
        assert "Cardiology" in data["certifications"]
        
        restored = Doctor.from_dict(data)
        assert restored.license_number == "LIC212"


class TestNurse:
    """Test Nurse-specific functionality."""

    def test_nurse_initialization(self):
        nurse = Nurse(
            "Nurse Johnson",
            "nur001",
            license_number="NL123",
            qualifications=["RN", "BLS"],
        )
        assert nurse.name == "Nurse Johnson"
        assert nurse.license_number == "NL123"
        assert len(nurse.qualifications) == 2
        assert len(nurse.vital_signs) == 0

    def test_update_vital_signs_new_patient(self):
        nurse = Nurse("Nurse Thompson", "nur002", license_number="NL456")
        
        result = nurse.update_vital_signs(
            "p1",
            {"temperature": 37.5, "heart_rate": 72, "blood_pressure": "120/80"},
        )
        assert result is True
        assert "p1" in nurse.vital_signs
        assert nurse.vital_signs["p1"].temperature == 37.5

    def test_update_vital_signs_existing_patient(self):
        nurse = Nurse("Nurse Anderson", "nur003", license_number="NL789")
        nurse.update_vital_signs("p1", {"temperature": 37.0})
        
        result = nurse.update_vital_signs("p1", {"temperature": 38.5})
        assert result is True
        assert nurse.vital_signs["p1"].temperature == 38.5

    def test_administer_medication(self):
        nurse = Nurse("Nurse Taylor", "nur004", license_number="NL101")
        
        result = nurse.administer_medication("p1", {"name": "Paracetamol", "dose": "500mg"})
        assert result is True

    def test_coordinate_care(self):
        nurse = Nurse("Nurse Thomas", "nur005", license_number="NL202")
        
        result = nurse.coordinate_care("p1", {"type": "observation", "notes": "Monitor overnight"})
        assert result is True

    def test_manage_food_deliveries_delivered(self):
        nurse = Nurse("Nurse Jackson", "nur006", license_number="NL303")
        delivery = FoodToDeliver(
            delivery_id="del001",
            food_items="Lunch Tray",
            room_number=101,
            scheduled_time=datetime.now(),
        )
        nurse.food_deliveries.append(delivery)
        
        result = nurse.manage_food_deliveries("del001", "delivered")
        assert result is True
        assert delivery.status == "delivered"

    def test_manage_food_deliveries_cancel(self):
        nurse = Nurse("Nurse White", "nur007", license_number="NL404")
        delivery = FoodToDeliver(
            delivery_id="del002",
            food_items="Dinner",
            room_number=102,
            scheduled_time=datetime.now(),
        )
        nurse.food_deliveries.append(delivery)
        
        result = nurse.manage_food_deliveries("del002", "cancel")
        assert result is True
        assert delivery.status == "cancelled"

    def test_create_food_delivery(self):
        nurse = Nurse("Nurse Harris", "nur008", license_number="NL505")
        scheduled = datetime.now() + timedelta(hours=1)
        
        delivery = nurse.create_food_delivery("p1", "Breakfast", 201, scheduled)
        assert delivery is not None
        assert delivery.food_items == "Breakfast"
        assert delivery.room_number == 201
        assert len(nurse.food_deliveries) == 1

    def test_view_pending_tasks(self):
        nurse = Nurse("Nurse Martin", "nur009", license_number="NL606")
        task1 = Task("t1", "Check vitals", "Desc", "high", "pending", datetime.now())
        task2 = Task("t2", "Administer meds", "Desc", "normal", "completed", datetime.now())
        task3 = Task("t3", "Update records", "Desc", "normal", "in-progress", datetime.now())
        nurse.tasks = [task1, task2, task3]
        
        pending = nurse.view_pending_tasks()
        assert len(pending) == 2
        assert task1 in pending
        assert task3 in pending
        assert task2 not in pending

    def test_mark_medication_administered(self):
        nurse = Nurse("Nurse Robinson", "nur010", license_number="NL707")
        
        result = nurse.mark_medication_administered("p1", {"name": "Insulin", "dose": "10 units"})
        assert result is True
        assert len(nurse.tasks) == 1
        assert nurse.tasks[0].status == "completed"
        assert "Insulin" in nurse.tasks[0].title

    def test_get_patient_vitals(self):
        nurse = Nurse("Nurse Clark", "nur011", license_number="NL808")
        nurse.update_vital_signs("p1", {"temperature": 37.2, "heart_rate": 68})
        
        vitals = nurse.get_patient_vitals("p1")
        assert "temperature" in vitals
        assert vitals["temperature"] == 37.2

    def test_get_patient_vitals_not_found(self):
        nurse = Nurse("Nurse Lewis", "nur012", license_number="NL909")
        
        vitals = nurse.get_patient_vitals("p999")
        assert vitals == {}

    def test_nurse_serialization(self):
        nurse = Nurse(
            "Nurse Walker",
            "nur013",
            license_number="NL010",
            qualifications=["RN", "ACLS"],
            work_to_do="Ward rounds",
        )
        data = nurse.to_dict()
        
        assert data["role"] == "nurse"
        assert data["licenseNumber"] == "NL010"
        assert "RN" in data["qualifications"]
        
        restored = Nurse.from_dict(data)
        assert restored.license_number == "NL010"


class TestIntegration:
    """Integration tests for carestaff workflows."""

    def test_doctor_nurse_collaboration(self):
        # Doctor diagnoses and prescribes
        doctor = Doctor("Dr. Smith", "doc100", license_number="LIC100")
        doctor.update_medical_details("p1", {"sickness_name": "Pneumonia"})
        doctor.prescribe_medication("p1", {"name": "Antibiotics"})
        
        # Nurse administers and monitors
        nurse = Nurse("Nurse Jones", "nur100", license_number="NL100")
        nurse.mark_medication_administered("p1", {"name": "Antibiotics"})
        nurse.update_vital_signs("p1", {"temperature": 38.5})
        
        # Verify workflow
        assert "Antibiotics" in doctor.patient_records["p1"].medications
        assert nurse.vital_signs["p1"].temperature == 38.5
        assert len(nurse.tasks) == 1

    def test_patient_assignment_workflow(self):
        staff = CareStaff("Staff Member", "cs100")
        
        # Assign multiple patients
        staff.assign_patient("p1")
        staff.assign_patient("p2")
        staff.assign_patient("p3")
        
        patients = staff.view_assigned_patients()
        assert len(patients) == 3
        
        # Unassign one
        staff.unassign_patient("p2")
        patients = staff.view_assigned_patients()
        assert len(patients) == 2
        assert "p2" not in patients

    def test_alert_handling_workflow(self):
        doctor = Doctor("Dr. Emergency", "doc101", license_number="LIC101")
        
        # Create and escalate
        doctor.escalate_to_specialist("p1", "Cardiology")
        assert len(doctor.alerts) == 1
        
        # Handle alert
        alert_id = doctor.alerts[0].alert_id
        doctor.handle_alert(alert_id, "acknowledge")
        assert doctor.alerts[0].acknowledged_at is not None
        
        # Resolve alert
        doctor.handle_alert(alert_id, "resolve")
        assert doctor.alerts[0].resolved_at is not None
