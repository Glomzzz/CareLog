from typing import List, Optional
import uuid
from datetime import datetime
from .patient import Patient
from .wellbeing_log import WellbeingLog
from .storage_service import StorageService

class CareLogService:
    def __init__(self):
        self.storage = StorageService()
        self.patients = self.storage.load("patients")
        self.logs = self.storage.load("wellbeing_logs")
        self.care_staff = self.storage.load("care_staff")
        
    def validate_registration(self, name: str, email: str, phone: str, password: str) -> tuple[bool, str]:
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

    def validate_wellbeing_log(self, pain_level: int, mood: str, appetite: str) -> tuple[bool, str]:
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

    def register_patient(self, name: str, email: str, phone: str, password: str) -> Patient:
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
        self.patients[patient_id] = patient_dict
        self.storage.save("patients", self.patients)
        return patient

    def login(self, email: str, password: str) -> Optional[Patient]:
        for patient_dict in self.patients.values():
            patient = Patient.patient_from_dict(patient_dict)
            if patient.get_decrypted_email() == email and patient.verify_password(password):
                return patient
        return None
    
    def add_wellbeing_log(self, patient_id: str, pain_level: int, mood: str, appetite: str, notes: str) -> WellbeingLog:
        """
        Add a new wellbeing log for a patient.
        Validates input and encrypts PHI fields.
        """
        is_valid, error = self.validate_wellbeing_log(pain_level, mood, appetite)
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
        self.logs[log_id] = log_dict
        self.storage.save("wellbeing_logs", self.logs)
        return log

    def get_patient_history(self, patient_id: str) -> List[WellbeingLog]:
        """
        Retrieve all wellbeing logs for a patient.
        Reconstructs logs for decryption.
        """
        patient_logs = []
        for log_dict in self.logs.values():
            if log_dict['patient_id'] != patient_id:
                continue
            log = WellbeingLog.from_dict(log_dict)
            patient_logs.append(log)
        return patient_logs

    def update_patient(self, patient_id: str, phone: str = None, email: str = None) -> Optional[Patient]:
        """
        Update patient profile fields (phone/email).
        Encrypts updated fields and saves changes.
        """
        if patient_id not in self.patients:
            return None
        patient_dict = self.patients[patient_id]
        patient = Patient.patient_from_dict(patient_dict)
        if phone is not None:
            patient.phone = patient.encrypt_field(phone)
        if email is not None:
            patient.email = patient.encrypt_field(email)
        self.patients[patient_id] = patient.to_dict()
        self.storage.save("patients", self.patients)
        return patient

    def search_care_staff(self, query: str) -> List[dict]:
        """
        Search care staff by name or medical field.
        Returns a list of matching staff dictionaries.
        """
        matching_staff = []
        query = query.lower()
        for staff_dict in self.care_staff.values():
            staff_name = staff_dict['name'].lower()
            staff_field = staff_dict['field'].lower()
            if query in staff_name or query in staff_field:
                matching_staff.append(staff_dict)
        return matching_staff
