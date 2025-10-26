from backend.services.carelog_service import CareLogService
from backend.models.patient import Patient
from backend.models.wellbeing_log import WellbeingLog

class PatientView:
    def show_main_menu(self):
        print("\nCareLog MVP")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        return input("Choose an option: ")

    def show_patient_menu(self, patient: Patient):
        # Always display the decrypted name
        decrypted_name = patient.get_decrypted_name()
        print(f"\nWelcome {decrypted_name}!")
        print("1. Add Wellbeing Log")
        print("2. View History")
        print("3. Update Profile")
        print("4. Search Care Staff")
        print("5. Logout")
        return input("Choose an option: ")

    def get_registration_details(self):
        name = input("Name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        password = input("Password: ")
        return name, email, phone, password

    def get_login_details(self):
        email = input("Email: ")
        password = input("Password: ")
        return email, password

    def get_wellbeing_log_details(self):
        pain_level = int(input("Pain Level (1-10): "))
        mood = input("Mood: ")
        appetite = input("Appetite: ")
        notes = input("Additional Notes: ")
        return pain_level, mood, appetite, notes

    def show_wellbeing_log(self, log: WellbeingLog):
        """
        Display decrypted wellbeing log information.
        Handles decryption errors gracefully.
        """
        try:
            decrypted_pain_level = log.get_decrypted_pain_level()
        except Exception:
            decrypted_pain_level = "(unable to decrypt)"
        try:
            decrypted_mood = log.get_decrypted_mood()
        except Exception:
            decrypted_mood = "(unable to decrypt)"
        try:
            decrypted_appetite = log.get_decrypted_appetite()
        except Exception:
            decrypted_appetite = "(unable to decrypt)"
        try:
            decrypted_notes = log.get_decrypted_notes()
        except Exception:
            decrypted_notes = "(unable to decrypt)"
        print(f"\nLog Date: {log.timestamp}")
        print(f"Pain Level: {decrypted_pain_level}")
        print(f"Mood: {decrypted_mood}")
        print(f"Appetite: {decrypted_appetite}")
        print(f"Notes: {decrypted_notes}")

    def get_profile_update_details(self):
        print("Leave blank if you don't want to update")
        email = input("New Email (or press Enter to skip): ")
        phone = input("New Phone (or press Enter to skip): ")
        return email if email else None, phone if phone else None

    def get_staff_search_query(self):
        return input("Enter search term (name or field): ")

    def show_staff_details(self, staff):
        print(f"\nName: {staff['name']}")
        print(f"Field: {staff['field']}")
        print(f"Contact: {staff['contact']}")
