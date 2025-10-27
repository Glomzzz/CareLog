import json
import pytest
from app.model.admin import Admin
from app.model.patient import Patient
from app.model.carestaff import CareStaff
from app.data.datastore import DataStore


@pytest.fixture(autouse=True)
def use_temp_datastore(tmp_path):
	"""Point DataStore to a temp file for each test and ensure it's initialized."""
	orig = DataStore.DATA_FILE
	DataStore.DATA_FILE = tmp_path / "carelog_test.json"
	# ensure file exists with initial structure
	DataStore.ensure_data_file()
	yield
	# restore
	DataStore.DATA_FILE = orig


def test_add_and_search_patient(capsys):
	admin = Admin()
	p = Patient(id="p1", name="Alice Example", email="alice@example.com", phone="012345", password="secret")
	# add via model instance
	admin.add_new_patients([p])

	stored = DataStore.get_by_id("patients", "id", "p1")
	assert stored is not None
	# ensure stored has expected keys
	assert stored.get("id") == "p1"
	assert "password_hash" in stored

	# search prints decrypted fields
	admin.search_patient_information("p1")
	captured = capsys.readouterr()
	assert "Alice Example" in captured.out


def test_update_patient_information():
	admin = Admin()
	p = Patient(id="p2", name="Bob Old", email="bob@old.com", phone="000111", password="pw1234")
	DataStore.append_to_collection("patients", p.to_dict())

	# update name
	result = admin.update_patients_information("p2", 1, "Bob New")
	assert result is True
	stored = DataStore.get_by_id("patients", "id", "p2")
	assert stored is not None
	p2 = Patient.patient_from_dict(stored)
	assert p2.get_decrypted_name() == "Bob New"


def test_remove_patients():
	admin = Admin()
	p1 = Patient(id="p3", name="Rem One", email="r1@example.com", phone="111", password="a12345")
	p2 = Patient(id="p4", name="Keep Two", email="k2@example.com", phone="222", password="b12345")
	DataStore.append_to_collection("patients", p1.to_dict())
	DataStore.append_to_collection("patients", p2.to_dict())

	admin.remove_patients(["p3"])  # remove first
	assert DataStore.get_by_id("patients", "id", "p3") is None
	assert DataStore.get_by_id("patients", "id", "p4") is not None


def test_add_update_remove_carestaff():
	admin = Admin()
	cs = CareStaff(name="Carol", carestaff_id="cs1", email="carol@x.com", password="pw")
	# add
	admin.add_new_carestaffs([cs])
	stored = DataStore.get_by_id("carestaffs", "id", "cs1")
	assert stored is not None
	assert stored.get("name") == "Carol"

	# update
	ok = admin.update_carestaffs_information("cs1", "Cardiology", "Cardio")
	assert ok is True
	stored = DataStore.get_by_id("carestaffs", "id", "cs1")
	assert stored.get("department") == "Cardiology"
	assert stored.get("specialization") == "Cardio"

	# remove
	admin.remove_carestaffs(["cs1"])
	assert DataStore.get_by_id("carestaffs", "id", "cs1") is None


def test_number_of_patients():
	admin = Admin()
	# create carestaff record with assigned patients
	cs_dict = {
		"id": "cs2",
		"name": "Dave",
		"email": "dave@x.com",
		"password": "",
		"department": "Ward",
		"specialization": "General",
		"assigned_patients": ["pA", "pB", "pC"],
	}
	DataStore.upsert("carestaffs", "id", cs_dict)
	assert admin.number_of_patients("cs2") == 3


def test_search_patients_by_keyword(capsys):
	admin = Admin()
	p = Patient(id="p5", name="John Smith", email="john.smith@example.com", phone="999888", password="pw12345")
	DataStore.append_to_collection("patients", p.to_dict())

	admin.search_patients_by_keyword("smith")
	out = capsys.readouterr().out
	assert "patient(s) found" in out or "p5" in out

