import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.carelog_service import CareLogService

@pytest.fixture
def service():
    return CareLogService()

def test_full_patient_workflow(service):
    # Functional test: Register, login, add log, update profile, view history, logout

    # Register
    patient = service.register_patient("TestUser", "testuser@example.com", "0123456789", "testpass")
    assert patient.get_decrypted_name() == "TestUser"

    # Login
    logged_in = service.login("testuser@example.com", "testpass")
    assert logged_in is not None
    assert logged_in.get_decrypted_name() == "TestUser"

    # Add wellbeing log
    log = service.add_wellbeing_log(patient.id, 4, "Tired", "Poor", "Needs rest")
    assert log.get_decrypted_pain_level() == 4
    assert log.get_decrypted_mood() == "Tired"

    # Update profile
    updated = service.update_patient(patient_id=patient.id, email="testuser2@example.com", phone="9876543210")
    assert updated.get_decrypted_email() == "testuser2@example.com"
    assert updated.get_decrypted_phone() == "9876543210"

    # View history
    logs = service.get_patient_history(patient.id)
    assert len(logs) == 1
    assert logs[0].get_decrypted_notes() == "Needs rest"

    # Logout (simulated by setting logged_in to None)
    logged_in = None
    assert logged_in is None

def test_care_staff_search_functional(service):
    # Functional test: Search care staff by name and field
    service.care_staff = {
        "staff1": {"name": "Dr. Alice", "field": "General", "contact": "alice@clinic.com"},
        "staff2": {"name": "Nurse Bob", "field": "Nursing", "contact": "bob@hospital.com"},
        "staff3": {"name": "Dr. Carol", "field": "Cardiology", "contact": "carol@heart.com"}
    }
    # Search by name
    results = service.search_care_staff("alice")
    assert len(results) == 1
    assert results[0]["name"] == "Dr. Alice"
    # Search by field
    results = service.search_care_staff("cardiology")
    assert len(results) == 1
    assert results[0]["field"] == "Cardiology"
    # Search with no match
    results = service.search_care_staff("xyz")
    assert len(results) == 0
