from app.carelog_service import CareLogService
from cli.patient_view import PatientView
from app.patient import Patient

def validate_choice(choice: str, valid_options: list) -> bool:
    """Validate if user input is one of the valid options"""
    return choice in valid_options

def main():
    # Initialize services and state
    service = CareLogService()
    view = PatientView()
    current_patient = None
    
    # Main application loop
    while True:
        choice = view.show_main_menu()
        
        # Validate main menu choice
        if not validate_choice(choice, ['1', '2', '3']):
            print("Invalid option! Please choose 1, 2, or 3")
            continue

        if choice == "1":
            # Patient Registration
            try:
                name, email, phone, password = view.get_registration_details()
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
                email, password = view.get_login_details()
                current_patient = service.login(email, password)
                
                if current_patient:
                    # Patient menu loop
                    while True:
                        # Pass the Patient object, not just the name
                        subchoice = view.show_patient_menu(current_patient)
                        
                        # Validate patient menu choice
                        if not validate_choice(subchoice, ['1', '2', '3', '4', '5']):
                            print("Invalid option! Please choose 1-5")
                            continue

                        if subchoice == "1":
                            # Add Wellbeing Log
                            try:
                                pain_level, mood, appetite, notes = view.get_wellbeing_log_details()
                                
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
                                from app.wellbeing_log import WellbeingLog
                                for log in logs:
                                    # logs are already WellbeingLog objects if get_patient_history is correct
                                    view.show_wellbeing_log(log)

                        elif subchoice == "3":
                            # Update Profile
                            try:
                                new_email, new_phone = view.get_profile_update_details()
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
                            query = view.get_staff_search_query()
                            if len(query.strip()) < 2:
                                print("Search term must be at least 2 characters!")
                                continue
                                
                            staff_list = service.search_care_staff(query)
                            if not staff_list:
                                print("No matching care staff found.")
                            for staff in staff_list:
                                view.show_staff_details(staff)

                        elif subchoice == "5":
                            # Logout
                            current_patient = None
                            print("Logged out successfully!")
                            break
                else:
                    print("Login failed!")
                    
            except Exception as e:
                print(f"Login error: {str(e)}")
                
        elif choice == "3":
            print("Thank you for using CareLog!")
            break

if __name__ == "__main__":
    main()
