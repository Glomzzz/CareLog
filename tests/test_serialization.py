from datetime import datetime
from pathlib import Path

from app.alerts import Alert, NotificationService
from app.assignment import PatientAssignment
from app.carestaff import CareStaff, Doctor, Nurse
from app.datastore import DataStore
from app.food import FoodToDeliver
from app.medical import MedicalDetails, PatientLog, VitalSigns
from app.schedule import Appointment, Schedule, Task
from app.user import User


def test_user_serialization_roundtrip():
    u = User(user_id="u1", name="Name", email="n@example.com", password="pw", role="patient")
    d = u.to_dict()
    u2 = User.from_dict(d)
    assert u2.user_id == u.user_id
    assert u2.email == u.email
    assert u2.role == u.role


def test_medical_details_log_vitals_serialization_roundtrip():
    md = MedicalDetails(
        record_id="r1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="staff1",
        sickness_name="Cold",
        department="General",
        severity="Mild",
        description="Desc",
        medications=["MedA"],
        treatments=["Treat1"],
        status="Pending",
    )
    mdd = md.to_dict()
    md2 = MedicalDetails.from_dict(mdd)
    assert md2.record_id == "r1"
    assert md2.sickness_name == "Cold"

    log = PatientLog(
        record_id="pl1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="staff2",
        personal_feeling="Good",
    )
    ld = log.to_dict()
    log2 = PatientLog.from_dict(ld)
    assert log2.record_id == "pl1"
    assert log2.personal_feeling == "Good"

    vs = VitalSigns(
        record_id="v1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="nurse1",
        measurement_id="m1",
        temperature=37.2,
        heart_rate=80,
        blood_pressure_systolic=120,
        blood_pressure_diastolic=80,
        respiratory_rate=16,
        oxygen_saturation=98.0,
        measured_at=datetime.now(),
    )
    vsd = vs.to_dict()
    vs2 = VitalSigns.from_dict(vsd)
    assert vs2.measurement_id == "m1"
    assert vs2.heart_rate == 80


def test_food_assignment_schedule_task_appointment_roundtrip():
    food = FoodToDeliver(
        delivery_id="dl1",
        food_items="Meal",
        room_number=101,
        scheduled_time=datetime.now(),
        status="scheduled",
    )
    fd = food.to_dict()
    food2 = FoodToDeliver.from_dict(fd)
    assert food2.delivery_id == "dl1"
    assert food2.room_number == 101

    pa = PatientAssignment(assignment_id="a1", assigned_date=datetime.now().date(), assignment_type="primary", notes="n")
    pad = pa.to_dict()
    pa2 = PatientAssignment.from_dict(pad)
    assert pa2.assignment_id == "a1"
    assert pa2.assignment_type == "primary"

    t = Task(task_id="t1", title="Check", description="desc", priority="normal", status="pending", due_date=datetime.now())
    td = t.to_dict()
    t2 = Task.from_dict(td)
    assert t2.task_id == "t1"
    assert t2.title == "Check"

    s = Schedule("c1", "TaskName", datetime.now().date().isoformat(), schedule_id="sid1", purpose="Purpose")
    sd = s.to_dict()
    s2 = Schedule.from_dict(sd)
    assert s2.schedule_id == "sid1"
    assert s2.purpose == "Purpose"

    ap = Appointment(appointment_id="ap1", patient_id="p1", date_and_time=datetime.now(), type="consultation")
    apd = ap.to_dict()
    ap2 = Appointment.from_dict(apd)
    assert ap2.appointment_id == "ap1"
    assert ap2.type == "consultation"


def test_alert_and_notification_service_roundtrip():
    alert = Alert(alert_id="al1", type="system", severity="high", message="msg")
    ad = alert.to_dict()
    alert2 = Alert.from_dict(ad)
    assert alert2.alert_id == "al1"
    assert alert2.severity == "high"

    ns = NotificationService(service_id="s1", channels=["email"], user_preferences={"u1": {"channel": "email"}})
    nsd = ns.to_dict()
    ns2 = NotificationService.from_dict(nsd)
    assert ns2.service_id == "s1"
    assert ns2.channels == ["email"]


def test_carestaff_doctor_nurse_roundtrip():
    cs = CareStaff(name="CS", carestaff_id="c1", email="c1@example.com", department="Gen", specialization="Spec")
    csd = cs.to_dict()
    cs2 = CareStaff.from_dict(csd)
    assert cs2.staff_id == cs.staff_id
    assert cs2.department == cs.department

    doc = Doctor(name="Doc", carestaff_id="d1", license_number="LIC1", certifications=["Cert1"], department="Cardio")
    dd = doc.to_dict()
    doc2 = Doctor.from_dict(dd)
    assert doc2.staff_id == doc.staff_id
    assert doc2.license_number == "LIC1"

    nurse = Nurse(name="Nurse", carestaff_id="n1", license_number="LN1", qualifications=["Q1"])
    nd = nurse.to_dict()
    nurse2 = Nurse.from_dict(nd)
    assert nurse2.staff_id == nurse.staff_id
    assert nurse2.license_number == "LN1"


def test_datastore_crud_roundtrip(tmp_path):
    # Point datastore to a temporary file for isolation
    temp_file = tmp_path / "carelog_ds.json"
    DataStore.DATA_FILE = temp_file

    # Ensure creating initial structure
    DataStore.ensure_data_file()
    all_data = DataStore.load_all()
    assert set(all_data.keys()) >= {"patients", "carestaffs", "notes", "schedules"}

    # Upsert + get
    patient_dict = {"patientID": "PX1", "name": "Pat X", "disease": "None", "high_risk": False}
    DataStore.upsert("patients", "patientID", patient_dict)
    fetched = DataStore.get_by_id("patients", "patientID", "PX1")
    assert fetched is not None and fetched["name"] == "Pat X"

    # Delete
    assert DataStore.delete_by_id("patients", "patientID", "PX1") is True
    assert DataStore.get_by_id("patients", "patientID", "PX1") is None
