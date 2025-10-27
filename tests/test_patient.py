import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime

from app.model.patient import Patient
from app.model.wellbeing_log import WellbeingLog
from app.carelog_service import CareLogService
from app.data.datastore import DataStore


# -------------------- Patient Tests (use mocked DataStore) --------------------


@pytest.fixture
def mock_datastore(monkeypatch):
    """Provide an in-memory datastore and monkeypatch DataStore classmethods.

    This keeps tests isolated from the filesystem by replacing the
    persistence layer with a small in-memory implementation.
    """
    store = {
        "patients": [],
        "wellbeing_logs": [],
        "notes": [],
        "schedules": [],
        "carestaffs": [
            {"id": "s1", "name": "Dr. Alice", "department": "General", "specialization": "General"},
            {"id": "s2", "name": "Nurse Bob", "department": "Nursing", "specialization": "Nursing"},
        ],
    }

    # Minimal replacements for DataStore methods used by CareLogService and models
    monkeypatch.setattr(DataStore, "load_all", classmethod(lambda cls: store))

    def save_all(cls, data):
        # Replace entire store contents
        store.clear()
        store.update(data)

    monkeypatch.setattr(DataStore, "save_all", classmethod(save_all))
    monkeypatch.setattr(DataStore, "get_collection", classmethod(lambda cls, name: store.get(name, [])))

    def upsert(cls, collection, id_key, item):
        items = store.setdefault(collection, [])
        key = item.get(id_key)
        if key is None:
            items.append(item)
            return
        for i, existing in enumerate(items):
            if isinstance(existing, dict) and existing.get(id_key) == key:
                items[i] = item
                return
        items.append(item)

    monkeypatch.setattr(DataStore, "upsert", classmethod(upsert))
    monkeypatch.setattr(
        DataStore,
        "get_by_id",
        classmethod(lambda cls, collection, id_key, id_value: next((it for it in store.get(collection, []) if isinstance(it, dict) and it.get(id_key) == id_value), None)),
    )
    def delete_by_id(cls, collection, id_key, id_value):
        items = store.get(collection, [])
        new_items = [it for it in items if not (isinstance(it, dict) and it.get(id_key) == id_value)]
        changed = len(new_items) != len(items)
        if changed:
            store[collection] = new_items
        return changed

    monkeypatch.setattr(DataStore, "delete_by_id", classmethod(delete_by_id))

    return store


@pytest.fixture
def patient_data():
    return {
        "id": "testid",
        "name": "Alice",
        "email": "alice@example.com",
        "phone": "0123456789",
        "password": "securepass",
    }


@pytest.fixture
def service(mock_datastore):
    # Ensure mock_datastore is applied before creating service
    return CareLogService()


def test_registration_valid(patient_data):
    patient = Patient(**patient_data)
    assert isinstance(patient, Patient)
    # Encrypted representation should differ from plain
    assert patient.name != patient_data["name"]


def test_password_hash_and_verify(patient_data):
    patient = Patient(**patient_data)
    assert patient.verify_password(patient_data["password"])
    assert not patient.verify_password("wrongpass")


def test_encryption_decryption(patient_data):
    patient = Patient(**patient_data)
    assert patient.get_decrypted_name() == patient_data["name"]
    assert patient.get_decrypted_email() == patient_data["email"]
    assert patient.get_decrypted_phone() == patient_data["phone"]


@pytest.mark.parametrize("field,value", [("id", ""), ("name", ""), ("email", ""), ("phone", ""), ("password", "")])
def test_missing_required_fields(field, value, patient_data):
    data = patient_data.copy()
    data[field] = value
    with pytest.raises(ValueError):
        Patient(**data)


def test_short_password(patient_data):
    data = patient_data.copy()
    data["password"] = "123"
    with pytest.raises(ValueError):
        Patient(**data)


def test_patient_from_dict(patient_data):
    patient = Patient(**patient_data)
    patient_dict = patient.to_dict()
    loaded = Patient.patient_from_dict(patient_dict)
    assert loaded.get_decrypted_name() == patient_data["name"]
    assert loaded.get_decrypted_email() == patient_data["email"]
    assert loaded.get_decrypted_phone() == patient_data["phone"]
    assert loaded.verify_password(patient_data["password"])


@pytest.fixture
def log_data():
    return {
        "id": "logid",
        "patient_id": "patientid",
        "timestamp": datetime.now(),
        "pain_level": 5,
        "mood": "Happy",
        "appetite": "Good",
        "notes": "Feeling fine",
    }


def test_log_encryption_decryption(log_data):
    log = WellbeingLog(**log_data)
    assert log.get_decrypted_pain_level() == 5
    assert log.get_decrypted_mood() == log_data["mood"]
    assert log.get_decrypted_appetite() == log_data["appetite"]
    assert log.get_decrypted_notes() == log_data["notes"]


def test_log_serialization_deserialization(log_data):
    log = WellbeingLog(**log_data)
    log_dict = log.to_dict()
    loaded = WellbeingLog.from_dict(log_dict)
    assert loaded.get_decrypted_pain_level() == 5
    assert loaded.get_decrypted_mood() == log_data["mood"]
    assert loaded.get_decrypted_appetite() == log_data["appetite"]
    assert loaded.get_decrypted_notes() == log_data["notes"]


@pytest.mark.parametrize("field,value", [("id", ""), ("patient_id", ""), ("timestamp", ""), ("pain_level", ""), ("mood", ""), ("appetite", ""), ("notes", "")])
def test_missing_required_fields_log(field, value, log_data):
    data = log_data.copy()
    data[field] = value
    with pytest.raises(ValueError):
        WellbeingLog(**data)


def test_registration_and_login(service):
    patient = service.register_patient("Bob", "bob@example.com", "0123456789", "bobpass")
    assert patient.get_decrypted_name() == "Bob"
    logged_in = service.login("bob@example.com", "bobpass")
    assert logged_in is not None
    assert logged_in.get_decrypted_name() == "Bob"
    assert service.login("bob@example.com", "wrongpass") is None


def test_add_and_get_wellbeing_log(service):
    patient = service.register_patient("Carol", "carol@example.com", "0123456789", "carolpass")
    log = service.add_wellbeing_log(patient.id, 8, "Sad", "Poor", "Needs help")
    assert log.get_decrypted_pain_level() == 8
    logs = service.get_patient_history(patient.id)
    assert len(logs) == 1
    assert logs[0].get_decrypted_mood() == "Sad"


def test_search_care_staff(service):
    results = service.search_care_staff("alice")
    assert len(results) >= 1
    assert any(r.get("name") == "Dr. Alice" for r in results)
    results = service.search_care_staff("nursing")
    assert len(results) >= 1
    assert any(r.get("specialization") == "Nursing" or r.get("department") == "Nursing" for r in results)
    results = service.search_care_staff("xyz")
    assert len(results) == 0


def test_update_profile(service):
    patient = service.register_patient("Eve", "eve@example.com", "0123456789", "evepass")
    updated = service.update_patient(patient_id=patient.id, email="eve2@example.com", phone="0987654321")
    assert updated is not None
    assert updated.get_decrypted_email() == "eve2@example.com"
    assert updated.get_decrypted_phone() == "0987654321"
    assert service.update_patient(patient_id="invalid_id", email="x@example.com") is None
