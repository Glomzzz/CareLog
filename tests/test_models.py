from datetime import datetime

from app.alerts import Alert, NotificationService
from app.assignment import PatientAssignment
from app.carestaff import CareStaff, Doctor, Nurse
from app.food import FoodToDeliver
from app.medical import PatientLog, VitalSigns
from app.patient import Diet, FamilyMember, Feedback, Patient
from app.schedule import Schedule, Task
from app.user import User


def test_user_login_logout_flow():
    user = User(user_id="u1", name="Test User", email="user@example.com", password="secret", role="patient")
    assert user.login({"email": "user@example.com", "password": "secret"}) is True
    assert user.is_logged_in is True
    user.logout()
    assert user.is_logged_in is False


def test_patient_feedback_and_schedule():
    patient = Patient(
        user_id="p1",
        name="Alice",
        email="alice@example.com",
        password="pwd",
        role="patient",
        emergency_contact="Bob",
        insurance_info="InsureCo",
        address="123 Health St",
        primary_diagnosis="Flu",
    )
    assert patient.give_feedback(5, "Great care") is True
    assert len(patient.feedback_entries) == 1

    appointment = patient.request_appointment({"date_and_time": datetime(2025, 1, 1, 10, 0), "type": "checkup"})
    assert appointment.type == "checkup"

    schedule = Schedule("c1", "Routine Check", "2025-01-02")
    patient.add_schedule(schedule)
    assert patient.view_schedule()[0].purpose == "Routine Check"


def test_diet_and_food_delivery():
    diet = Diet(diet_id="d1", allergies=["nuts"])
    patient = Patient(
        user_id="p2",
        name="John",
        email="john@example.com",
        password="pwd",
        role="patient",
        emergency_contact="Jane",
        insurance_info="InsureCo",
        address="456 Wellness Ave",
        diet=diet,
    )
    delivery = FoodToDeliver(
        delivery_id="del1",
        food_items="Nut-Free Meal",
        room_number=101,
        scheduled_time=datetime.utcnow(),
    )
    assert delivery.verify_allergies(patient) is True
    assert delivery.update_delivery_status("delivered") is True


def test_carestaff_and_task_management(monkeypatch):
    staff = CareStaff("Nora", "c1", department="General", specialization="Care")
    task = Task(
        task_id="t1",
        title="Check Vitals",
        description="Morning rounds",
        priority="normal",
        status="pending",
        due_date=datetime(2025, 1, 3, 8, 0),
    )

    store = {"patients": [], "notes": [], "schedules": []}

    monkeypatch.setattr(CareStaff, "_load_data", lambda self: store)
    monkeypatch.setattr(CareStaff, "_save_data", lambda self, data: store.update(data))

    assert task.assign_task(staff) is True
    assert staff.tasks[0].task_id == "t1"

    staff.assigned_patients.append("p1")
    task.mark_complete()
    report = staff.generate_reports(datetime(2025, 1, 1), datetime(2025, 1, 31))
    assert report["patients_managed"] == "1"
    assert report["tasks_completed"] == "1"

    staff.add_schedule("Medication", "2025-01-04")
    assert len(store["schedules"]) == 1


def test_doctor_and_nurse_specialisations():
    doctor = Doctor("Dr. Who", "d1", license_number="LIC123", department="Cardiology")
    assert doctor.update_medical_details("p1", {"description": "Initial consult", "medications": ["MedA"]}) is True
    assert doctor.prescribe_medication("p1", {"name": "MedB"}) is True
    assert doctor.approve_treatment_plans("p1", {"status": "approved"}) is True
    assert doctor.escalate_to_specialist("p1", "Neurology") is True

    nurse = Nurse("Nina", "n1", license_number="LN001")
    assert nurse.update_vital_signs("p1", {"temperature": 38.5}) is True
    assert nurse.coordinate_care("p1", {"type": "observation"}) is True
    assert "High temperature" in nurse.vital_signs["p1"].detect_anomalies()


def test_alerts_and_notifications():
    alert = Alert(alert_id="a1", type="system", severity="medium", message="Check system logs")
    user = User(user_id="u2", name="Ops", email="ops@example.com", password="pw", role="admin")
    assert alert.acknowledge_alert(user) is True
    assert alert.calculate_priority() == "P2"

    notifier = NotificationService(service_id="svc1", channels=["email"])
    assert notifier.send_immediate_alert(user, "Test message") is True
    assert notifier.batch_notify([user], "Reminder") is True


def test_patient_assignment_and_family_member():
    assignment = PatientAssignment(
        assignment_id="assign1",
        assigned_date=datetime(2025, 1, 1).date(),
        assignment_type="primary",
    )
    assert assignment.assign_patient("p2", "c2") is True
    assert assignment.transfer_patient("p2", "c3") is True
    assert assignment.end_assignment("p2") is True

    patient = Patient(
        user_id="p3",
        name="Mia",
        email="mia@example.com",
        password="pwd",
        role="patient",
        emergency_contact="Max",
        insurance_info="InsureCo",
        address="789 Care Blvd",
        diet=Diet(diet_id="d2", food_preferences=["Soup"]),
    )
    family = FamilyMember(
        user_id="fam1",
        name="Liam",
        email="liam@example.com",
        password="pwd",
        role="family",
        relationship="Brother",
        contact_info="12345678",
        linked_patients=[patient],
    )
    status = family.view_patient_status("p3")
    assert status["status"] == "admitted"
    assert family.provide_feedback("p3", {"rating": 4, "comments": "Thanks"}) is True


def test_feedback_and_medical_logs():
    feedback = Feedback(feedback_id="fb1", rating=3, comments="Average")
    user = User(user_id="u3", name="Reporter", email="rep@example.com", password="pw", role="staff")
    assert feedback.submit_feedback(user, {"rating": 5, "comments": "Great"}) is True
    assert feedback.analyze_sentiment() == "positive"

    log = PatientLog(
        record_id="log1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="staff1",
    )
    assert log.update_personal_feeling("Happy") is True
    assert log.add_feedback("Feeling better") is True

    vitals = VitalSigns(
        record_id="v1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="staff2",
    )
    assert vitals.record_vitals({"temperature": 37.5, "heart_rate": 80}) is True