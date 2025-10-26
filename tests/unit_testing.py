import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime
from app.patient import Patient
from app.wellbeing_log import WellbeingLog
from app.carelog_service import CareLogService

# -------------------- Patient Tests --------------------

@pytest.fixture
def patient_data():
    # Sample patient data for tests
    return {
        "id": "testid",
        "name": "Alice",
        "email": "alice@example.com",
        "phone": "0123456789",
        "password": "securepass"
    }

def test_registration_valid(patient_data):
    # Positive test: valid registration
    patient = Patient(**patient_data)
    assert isinstance(patient, Patient)
    assert patient.name != patient_data["name"]  # Should be encrypted

def test_password_hash_and_verify(patient_data):
    # Positive test: correct password
    patient = Patient(**patient_data)
    assert patient.verify_password(patient_data["password"])
    # Negative test: incorrect password
    assert not patient.verify_password("wrongpass")

def test_encryption_decryption(patient_data):
    # Positive test: encryption and decryption of PHI fields
    patient = Patient(**patient_data)
    assert patient.get_decrypted_name() == patient_data["name"]
    assert patient.get_decrypted_email() == patient_data["email"]
    assert patient.get_decrypted_phone() == patient_data["phone"]

@pytest.mark.parametrize("field,value", [
    ("id", ""), ("name", ""), ("email", ""), ("phone", ""), ("password", "")
])
def test_missing_required_fields(field, value, patient_data):
    # Negative test: missing required fields should raise ValueError
    data = patient_data.copy()
    data[field] = value
    with pytest.raises(ValueError):
        Patient(**data)

def test_short_password(patient_data):
    # Negative test: password too short should raise ValueError
    data = patient_data.copy()
    data["password"] = "123"
    with pytest.raises(ValueError):
        Patient(**data)

def test_patient_from_dict(patient_data):
    # Positive test: serialization and deserialization
    patient = Patient(**patient_data)
    patient_dict = patient.to_dict()
    loaded = Patient.patient_from_dict(patient_dict)
    assert loaded.get_decrypted_name() == patient_data["name"]
    assert loaded.get_decrypted_email() == patient_data["email"]
    assert loaded.get_decrypted_phone() == patient_data["phone"]
    assert loaded.verify_password(patient_data["password"])

# -------------------- WellbeingLog Tests --------------------

@pytest.fixture
def log_data():
    # Sample wellbeing log data for tests
    return {
        "id": "logid",
        "patient_id": "patientid",
        "timestamp": datetime.now(),
        "pain_level": 5,
        "mood": "Happy",
        "appetite": "Good",
        "notes": "Feeling fine"
    }

def test_log_encryption_decryption(log_data):
    # Positive test: encryption and decryption of PHI fields
    log = WellbeingLog(**log_data)
    assert log.get_decrypted_pain_level() == 5
    assert log.get_decrypted_mood() == log_data["mood"]
    assert log.get_decrypted_appetite() == log_data["appetite"]
    assert log.get_decrypted_notes() == log_data["notes"]

def test_log_serialization_deserialization(log_data):
    # Positive test: serialization and deserialization
    log = WellbeingLog(**log_data)
    log_dict = log.to_dict()
    loaded = WellbeingLog.from_dict(log_dict)
    assert loaded.get_decrypted_pain_level() == 5
    assert loaded.get_decrypted_mood() == log_data["mood"]
    assert loaded.get_decrypted_appetite() == log_data["appetite"]
    assert loaded.get_decrypted_notes() == log_data["notes"]

@pytest.mark.parametrize("field,value", [
    ("id", ""), ("patient_id", ""), ("timestamp", ""), ("pain_level", ""), ("mood", ""), ("appetite", ""), ("notes", "")
])
def test_missing_required_fields_log(field, value, log_data):
    # Negative test: missing required fields should raise ValueError
    data = log_data.copy()
    data[field] = value
    with pytest.raises(ValueError):
        WellbeingLog(**data)

# -------------------- CareLogService Tests --------------------

@pytest.fixture
def service():
    return CareLogService()

def test_registration_and_login(service):
    # Positive test: Register and login with correct credentials
    patient = service.register_patient("Bob", "bob@example.com", "0123456789", "bobpass")
    assert patient.get_decrypted_name() == "Bob"
    logged_in = service.login("bob@example.com", "bobpass")
    assert logged_in is not None
    assert logged_in.get_decrypted_name() == "Bob"
    # Negative test: Login with wrong password
    assert service.login("bob@example.com", "wrongpass") is None

def test_add_and_get_wellbeing_log(service):
    # Positive test: Add and retrieve wellbeing log
    patient = service.register_patient("Carol", "carol@example.com", "0123456789", "carolpass")
    log = service.add_wellbeing_log(patient.id, 8, "Sad", "Poor", "Needs help")
    assert log.get_decrypted_pain_level() == 8
    logs = service.get_patient_history(patient.id)
    assert len(logs) == 1
    assert logs[0].get_decrypted_mood() == "Sad"

def test_search_care_staff(service):
    # Positive test: Search by name and field
    service.care_staff = {
        "staff1": {"name": "Dr. Alice", "field": "General", "contact": "alice@clinic.com"},
        "staff2": {"name": "Nurse Bob", "field": "Nursing", "contact": "bob@hospital.com"}
    }
    results = service.search_care_staff("alice")
    assert len(results) == 1
    assert results[0]["name"] == "Dr. Alice"
    results = service.search_care_staff("nursing")
    assert len(results) == 1
    assert results[0]["field"] == "Nursing"
    # Negative test: Search with no match
    results = service.search_care_staff("xyz")
    assert len(results) == 0

def test_update_profile(service):
    # Positive test: update email and phone
    patient = service.register_patient("Eve", "eve@example.com", "0123456789", "evepass")
    updated = service.update_patient(patient_id=patient.id, email="eve2@example.com", phone="0987654321")
    assert updated is not None
    assert updated.get_decrypted_email() == "eve2@example.com"
    assert updated.get_decrypted_phone() == "0987654321"
    # Negative test: invalid patient_id
    assert service.update_patient(patient_id="invalid_id", email="x@example.com") is None
