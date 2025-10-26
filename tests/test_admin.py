import json
import pytest
from unittest.mock import mock_open, patch
from app.admin import Admin

@pytest.fixture
def admin_instance():
    """Fixture to create a reusable Admin instance."""
    return Admin("JT", "A6", "012-6783782", "jt0203@gmail.com", "jt060203")

@pytest.fixture
def mock_data():
    """Mock CareLog JSON structure."""
    return {
        "admins": [
            {"adminID": "A6", 
             "name": "JT", 
             "phone": "012-6783782", 
             "email": "jt0203@gmail.com", 
             "password": "jt060203"}
        ],
        "patients": [
            {"patientID": "P5", 
             "name": "Alice", 
             "email": "alice@mail.com", 
             "phone": "015-8749274", 
             "password": "aliceinwonderland"}
        ],
        "carestaffs": [
            {"staffID": "D64", 
             "department": "Department A", 
             "specialization": "Neurology", 
             "assignedPatients": ["P5"], 
             "workSchedule": ""}
        ]
    }


# 1. Add new patients
def test_add_new_patients(admin_instance, mock_data):
    new_patients = [
        {"patientID": "P6", 
         "name": "Bob", 
         "email": "bob083@gmail.com", 
         "phone": "019-7207523", 
         "password": "bobbobbob"}
    ]
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.add_new_patients(new_patients)

    # Verify it appended new patient to the mock data
    written_str = "".join(call.args[0] for call in m().write.call_args_list)
    written_data = json.loads(written_str)
    assert any(p["patientID"] == "P6" for p in written_data["patients"])


# 2. Update patients information
def test_update_patients_information_success(admin_instance, mock_data):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.update_patients_information("P5", 1, "Alice Updated")

    written_str = "".join(call.args[0] for call in m().write.call_args_list)
    written_data = json.loads(written_str)
    assert written_data["patients"][0]["name"] == "Alice Updated"


def test_update_patients_information_not_found(admin_instance, mock_data, capsys):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.update_patients_information("P999", 1, "New Name")
    captured = capsys.readouterr()
    assert "Patient not found" in captured.out


# 3. Remove patients
def test_remove_patients_success(admin_instance, mock_data):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.remove_patients(["P5"])

    written_str = "".join(call.args[0] for call in m().write.call_args_list)
    written_data = json.loads(written_str)
    assert all(p["patientID"] != "P5" for p in written_data["patients"])


# 4. Add new carestaffs
def test_add_new_carestaffs(admin_instance, mock_data):
    new_carestaffs = [
        {"staffID": "N54", "department": "Department C", "specialization": "Neurology", "assignedPatients": [], "workSchedule": ""}
    ]
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.add_new_carestaffs(new_carestaffs)
    written_str = "".join(call.args[0] for call in m().write.call_args_list)
    written_data = json.loads(written_str)
    assert any(s["staffID"] == "N54" for s in written_data["carestaffs"])


# 5. Update carestaffs information
def test_update_carestaffs_information_success(admin_instance, mock_data):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.update_carestaffs_information("D64", "Department Z", "Dermatology")
    written_str = "".join(call.args[0] for call in m().write.call_args_list)
    written_data = json.loads(written_str)
    staff = written_data["carestaffs"][0]
    assert staff["department"] == "Department Z"
    assert staff["specialization"] == "Dermatology"


def test_update_carestaffs_information_not_found(admin_instance, mock_data, capsys):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.update_carestaffs_information("D100", "Department C", "Urology")
    captured = capsys.readouterr()
    assert "Carestaff not found" in captured.out


# 6. Remove carestaffs
def test_remove_carestaffs_success(admin_instance, mock_data):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.remove_carestaffs(["D64"])
    written_str = "".join(call.args[0] for call in m().write.call_args_list)
    written_data = json.loads(written_str)
    assert all(s["staffID"] != "D64" for s in written_data["carestaffs"])


# 7. Search patient information
def test_search_patient_information_found(admin_instance, mock_data, capsys):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.search_patient_information("P5")
    captured = capsys.readouterr()
    assert "Patient found!" in captured.out


def test_search_patient_information_not_found(admin_instance, mock_data, capsys):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        admin_instance.search_patient_information("P98")
    captured = capsys.readouterr()
    assert "Patient not found" in captured.out


# 8. Test to get number of patients for a carestaff
def test_number_of_patients_found(admin_instance, mock_data):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        num = admin_instance.number_of_patients("D64")
    assert num == 1


def test_number_of_patients_not_found(admin_instance, mock_data):
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        result = admin_instance.number_of_patients("D98")
    assert result is None