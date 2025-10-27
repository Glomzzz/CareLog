from typing import List, Optional
import uuid
from datetime import datetime
from .model.patient import Patient
from .model.wellbeing_log import WellbeingLog
from .data.datastore import DataStore

class CareLogService:
    
    @classmethod
    def validate_registration(cls, name: str, email: str, phone: str, password: str) -> tuple[bool, str]:
        """
        Validate registration data.
        Checks for required fields, email format, password length, and phone digits.
        Returns: (is_valid: bool, error_message: str)
        """
        if not all([name, email, phone, password]):
            return False, "All fields are required"
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        if not phone.isdigit():
            return False, "Phone must contain only numbers"
        return True, ""

    @classmethod
    def validate_wellbeing_log(cls, pain_level: int, mood: str, appetite: str) -> tuple[bool, str]:
        """
        Validate wellbeing log data.
        Checks pain level range and required mood/appetite.
        Returns: (is_valid: bool, error_message: str)
        """
        if not isinstance(pain_level, int) or not 1 <= pain_level <= 10:
            return False, "Pain level must be between 1 and 10"
        if not mood:
            return False, "Mood is required"
        if not appetite:
            return False, "Appetite status is required"
        return True, ""

    @classmethod
    def register_patient(cls, name: str, email: str, phone: str, password: str) -> Patient:
        patient_id = str(uuid.uuid4())
        patient = Patient(
            id=patient_id,
            name=name,
            email=email,
            phone=phone,
            password=password,
            # key and iv will be generated automatically
            encrypted=False  # Fields are not encrypted yet
        )
        patient_dict = patient.to_dict()
        DataStore.upsert("patients", "id", patient_dict)
        return patient

    @classmethod
    def login(cls, email: str, password: str) -> Optional[Patient]:
        for patient_dict in DataStore.get_collection("patients"):
            patient = Patient.patient_from_dict(patient_dict)
            if patient.get_decrypted_email() == email and patient.verify_password(password):
                return patient
        return None

    @classmethod
    def add_wellbeing_log(cls, patient_id: str, pain_level: int, mood: str, appetite: str, notes: str) -> WellbeingLog:
        """
        Add a new wellbeing log for a patient.
        Validates input and encrypts PHI fields.
        """
        is_valid, error = cls.validate_wellbeing_log(pain_level, mood, appetite)
        if not is_valid:
            raise ValueError(error)
        log_id = str(uuid.uuid4())
        current_time = datetime.now()
        log = WellbeingLog(
            id=log_id,
            patient_id=patient_id,
            timestamp=current_time,
            pain_level=str(pain_level),  # Ensure pain_level is a string before encryption
            mood=mood,
            appetite=appetite,
            notes=notes
        )
        log_dict = log.to_dict()
        DataStore.upsert("wellbeing_logs", "id", log_dict)
        return log

    @classmethod
    def get_patient_history(cls, patient_id: str) -> List[WellbeingLog]:
        """
        Retrieve all wellbeing logs for a patient.
        Reconstructs logs for decryption.
        """
        patient_logs = []
        for log_dict in DataStore.get_collection("wellbeing_logs"):
            if log_dict['patient_id'] != patient_id:
                continue
            log = WellbeingLog.from_dict(log_dict)
            patient_logs.append(log)
        return patient_logs

    @classmethod
    def update_patient(cls, patient_id: str, phone: str = None, email: str = None) -> Optional[Patient]:
        """
        Update patient profile fields (phone/email).
        Encrypts updated fields and saves changes.
        """
        patients = DataStore.get_collection("patients")
        patient_dict = None
        for pd in patients:
            if pd['id'] == patient_id:
                patient_dict = pd
                break
        if patient_dict is None:
            return None
        patient = Patient.patient_from_dict(patient_dict)
        if phone is not None:
            patient.phone = patient.encrypt_field(phone)
        if email is not None:
            patient.email = patient.encrypt_field(email)
        patient_dict = patient.to_dict()
        DataStore.upsert("patients", "id", patient_dict)
        return patient

    @classmethod
    def search_care_staff(cls, query: str) -> List[dict]:
        """
        Search care staff by name or medical field.
        Returns a list of matching staff dictionaries.
        """
        matching_staff = []
        query = query.lower()
        for staff_dict in DataStore.get_collection("carestaffs"):
            print(staff_dict)
            staff_name = staff_dict['name'].lower()
            staff_department = staff_dict['department'].lower()
            staff_specialization = staff_dict['specialization'].lower()
            if query in staff_name or query in staff_department or query in staff_specialization:
                matching_staff.append(staff_dict)
        return matching_staff
