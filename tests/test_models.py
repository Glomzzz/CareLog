from datetime import datetime

from app.model.alerts import Alert, NotificationService
from app.model.carestaff import CareStaff, Doctor, Nurse
from app.model.schedule import Task
from app.model.user import User


def test_user_login_logout_flow():
    user = User(user_id="u1", name="Test User", email="user@example.com", password="secret", role="patient")
    assert user.login({"email": "user@example.com", "password": "secret"}) is True
    assert user.is_logged_in is True
    user.logout()
    assert user.is_logged_in is False


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
