import json
import pytest
import os
from app.carestaff import CareStaff

TEST_DATA_PATH = "data/carelog_test.json"

@pytest.fixture
def sample_data():
    return {
        "patients": [
            {
                "patientID": "P1",
                "name": "Alice Nguyen",
                "disease": "Flu",
                "high_risk": False
            }
        ],
        "carestaffs": [
            {
                "carestaffID": "C1",
                "name": "Test Staff",
                "password": "123"
            }
        ],
        "notes": [],
        "schedules": []
    }

@pytest.fixture
def mock_carestaff(monkeypatch, sample_data):
    os.makedirs("data", exist_ok=True)
    with open(TEST_DATA_PATH, "w") as f:
        json.dump(sample_data, f, indent=4)

    def fake_load(self):
        with open(TEST_DATA_PATH, "r") as f:
            return json.load(f)

    def fake_save(self, data):
        with open(TEST_DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)

    monkeypatch.setattr(CareStaff, "_load_data", fake_load)
    monkeypatch.setattr(CareStaff, "_save_data", fake_save)

    return CareStaff("Test Staff", "C1")
    
def test_add_note(mock_carestaff):
    mock_carestaff.add_note("P1", "Feeling better")
    data = mock_carestaff._load_data()
    assert len(data["notes"]) == 1
    assert data["notes"][0]["content"] == "Feeling better"


def test_update_disease(mock_carestaff):
    mock_carestaff.update_disease("P1", "Covid-19")
    data = mock_carestaff._load_data()
    assert data["patients"][0]["disease"] == "Covid-19"


def test_toggle_high_risk(mock_carestaff):
    data = mock_carestaff._load_data()
    assert data["patients"][0]["high_risk"] is False

    mock_carestaff.toggle_high_risk("P1")
    data = mock_carestaff._load_data()
    assert data["patients"][0]["high_risk"] is True

    mock_carestaff.toggle_high_risk("P1")
    data = mock_carestaff._load_data()
    assert data["patients"][0]["high_risk"] is False


def test_search_patient_output(mock_carestaff, capsys):
    mock_carestaff.search_patient("Alice")
    captured = capsys.readouterr()
    assert "Alice Nguyen" in captured.out


def test_view_notes_output(mock_carestaff, capsys):
    mock_carestaff.add_note("P1", "Test viewing notes")
    mock_carestaff.view_notes("P1")
    captured = capsys.readouterr()
    assert "Test viewing notes" in captured.out


def test_add_schedule(mock_carestaff):
    mock_carestaff.add_schedule("Check BP", "2025-10-25")
    data = mock_carestaff._load_data()
    assert len(data["schedules"]) == 1
    assert data["schedules"][0]["task"] == "Check BP"
