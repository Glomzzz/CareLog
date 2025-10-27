from app.carelog_service import CareLogService
from app.model.patient import Patient
from app.model.wellbeing_log import WellbeingLog


class PatientCli:
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
    
    def run(self):
        # Initialize services and state
        service = CareLogService()
        current_patient = None
        
        # Main application loop
        while True:
            choice = self.show_main_menu()
            
            # Validate main menu choice
            if not validate_choice(choice, ['1', '2', '3']):
                print("Invalid option! Please choose 1, 2, or 3")
                continue

            if choice == "1":
                # Patient Registration
                try:
                    name, email, phone, password = self.get_registration_details()
                    # Validate registration input before creating patient
                    is_valid, error = service.validate_registration(name, email, phone, password)
                    if not is_valid:
                        print(f"Registration failed: {error}")
                        continue
                    patient = service.register_patient(name, email, phone, password)
                    print(f"Registered successfully! Your ID is {patient.id}")
                except ValueError as e:
                    print(f"Registration failed: {str(e)}")
                
            elif choice == "2":
                # Patient Login
                try:
                    email, password = self.get_login_details()
                    current_patient = service.login(email, password)
                    
                    if current_patient:
                        # Patient menu loop
                        while True:
                            # Pass the Patient object, not just the name
                            subchoice = self.show_patient_menu(current_patient)
                            
                            # Validate patient menu choice
                            if not validate_choice(subchoice, ['1', '2', '3', '4', '5']):
                                print("Invalid option! Please choose 1-5")
                                continue

                            if subchoice == "1":
                                # Add Wellbeing Log
                                try:
                                    pain_level, mood, appetite, notes = self.get_wellbeing_log_details()
                                    
                                    # Validate pain level
                                    if not 1 <= pain_level <= 10:
                                        print("Pain level must be between 1 and 10!")
                                        continue
                                    
                                    log = service.add_wellbeing_log(
                                        current_patient.id, pain_level, mood, appetite, notes
                                    )
                                    print("Wellbeing log added successfully!")
                                    
                                except ValueError:
                                    print("Invalid pain level! Please enter a number between 1-10")

                            elif subchoice == "2":
                                # View Patient History
                                logs = service.get_patient_history(current_patient.id)
                                if not logs:
                                    print("No history found.")
                                else:
                                    # Ensure logs are reconstructed for decryption
                                    from app.model.wellbeing_log import WellbeingLog
                                    for log in logs:
                                        # logs are already WellbeingLog objects if get_patient_history is correct
                                        self.show_wellbeing_log(log)

                            elif subchoice == "3":
                                # Update Profile
                                try:
                                    new_email, new_phone = self.get_profile_update_details()
                                    if new_email and '@' not in new_email:
                                        print("Invalid email format!")
                                        continue
                                    
                                    if new_email or new_phone:
                                        updated_patient = service.update_patient(
                                            patient_id=current_patient.id,
                                            phone=new_phone,
                                            email=new_email
                                        )
                                        if updated_patient:
                                            # Reconstruct Patient object to ensure decrypted display
                                            current_patient = Patient.patient_from_dict(updated_patient.to_dict())
                                            print("Profile updated successfully!")
                                        else:
                                            print("Update failed!")
                                except Exception as e:
                                    print(f"Update failed: {str(e)}")

                            elif subchoice == "4":
                                # Search Care Staff
                                query = self.get_staff_search_query()
                                if len(query.strip()) < 2:
                                    print("Search term must be at least 2 characters!")
                                    continue
                                    
                                staff_list = service.search_care_staff(query)
                                if not staff_list:
                                    print("No matching care staff found.")
                                for staff in staff_list:
                                    self.show_staff_details(staff)

                            elif subchoice == "5":
                                # Logout
                                current_patient = None
                                print("Logged out successfully!")
                                break
                            
                            input("Press Enter to continue...")
                    else:
                        print("Login failed!")
                        input("Press Enter to continue...")
                except Exception as e:
                    print(f"Login error: {str(e)}")
                    
            elif choice == "3":
                print("Thank you for using CareLog!")
                break
            input("Press Enter to continue...")

def validate_choice(choice: str, valid_options: list) -> bool:
    """Validate if user input is one of the valid options"""
    return choice in valid_options