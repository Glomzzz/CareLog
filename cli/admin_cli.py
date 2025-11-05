from colorama import Fore
from app.model.admin import Admin
from app.model.patient import Patient

class AdminCLI:
    
    def register(self):
        """Register a new admin."""
        print(Fore.CYAN + "\n=== Admin Registration ===")
        admin_id = input("Enter Admin ID: ").strip()
        name = input("Enter Full Name: ").strip()
        phone = input("Enter Phone Number: ").strip()
        email = input("Enter Email: ").strip()
        password = input("Enter Password: ").strip()
        # Admin.register signature expects (name, id, email, password, phone)
        new_admin = Admin.register(
            name,
            admin_id,
            email,
            password,
            phone,
        )

        if new_admin:
            # Persisted record uses the provided admin_id as the identifier.
            print(Fore.GREEN + f"✓ Registration successful! Your Admin ID is {admin_id}")
            self.current_admin = new_admin
        else:
            print(Fore.RED + "✗ Registration failed. Please try again.")

    def login(self):
        """Handle admin login."""
        print(Fore.CYAN + "\n=== Admin Login ===")
        admin_id = input("Enter Admin ID: ").strip()

        self.current_admin = Admin.get_admin_by_id(admin_id)
        if not self.current_admin:
            print(Fore.RED + "✗ Admin not found. Please check the Admin ID.")
            return
        password = input("Enter Password: ").strip()

        # Attempt login
        credentials = {"email": self.current_admin.email, "password": password}
        if self.current_admin.login(credentials):
            print(Fore.GREEN + f"\n✓ Welcome, Admin {self.current_admin.name}!")
        else:
            print(Fore.RED + "✗ Login failed. Please check credentials.")
            self.current_admin = None
    
    def run(self):
        print("[ADMIN'S CARELOG PAGE] Welcome!")

        admin_ids = Admin.all_admin_ids()
        
        if not admin_ids:
            print("No admin accounts found. Please register a new admin account.")
            self.register()
            if not self.current_admin:
                print("Registration failed. Exiting.")
                return
        else:
            self.login()
            if not self.current_admin:
                print("Login failed. Exiting.")
                return

        print(f"Login successful! Welcome back {self.current_admin.name}! ")
        admin_on = True
        while admin_on:
            print("[ADMIN'S MAIN MENU]")
            print("1. Add patient(s).")
            print("2. Update patient's information.")
            print("3. Remove patient(s).")
            print("4. Update carestaff's information.")
            print("5. Remove carestaff(s).")
            print("6. Get patient's information or record.")
            print("7. Get the number of patients for all the carestaffs has.")
            print("8. Log out.")

            choice = int(input("Enter your choice: "))

            if choice == 1:
                number_of_patients = int(input("Enter the number of patients that you want to add: "))

                new_patients_list = []
                for i in range(number_of_patients):
                    print(f"You are entering details for patient number {i + 1}.")
                    id = str(input("Enter the patient ID assigned to the new patient: "))
                    name = str(input("Enter patient's name: "))
                    email = str(input("Enter patient's email: "))
                    phone = str(input("Enter patient's phone: "))
                    print("The default password hash for the patient is [abcd1234] - patient can change it themselves afterwards.")
                    # Create new patient, add it into list of patients
                    new_patients_list.append(
                        Patient(name, id, phone, email).to_dict()
                    )
                self.current_admin.add_new_patients(new_patients_list)
            
            elif choice == 2:
                id = str(input("Enter the patient ID of the patient's information that you want to change: "))
                print("Which information do you want to change? ")
                print("1. Patient's name.")
                print("2. Patient's email.")
                print("3. Patient's phone.")
                choice = int(input("Enter your choice: "))
                information = str(input("What do you want to change it to: "))

                self.current_admin.update_patients_information(id, choice, information)

            elif choice == 3:
                number_of_patients = int(input("Enter the number of patients that you want to remove: "))

                id_list = []
                print("Please enter the patient ID of the patient that you want to delete - one by one.")
                for i in range(number_of_patients):
                    id = str(input(f"{i+1}: "))
                    id_list.append(id)
                
                self.current_admin.remove_patients(id_list)

            elif choice == 4:
                id = str(input("Enter the carestaff ID of the carestaff's information that you want to change: "))
                department = None
                specialization = None
                
                if(input("Update Carestaff's department? (y/n): ")=='y'):
                    department = str(input("What do you want to change it to: "))
                if(input("Update Carestaff's specialization? (y/n): ")=='y'):
                    specialization = str(input("What do you want to change it to: "))
                if not self.current_admin.update_carestaffs_information(id, department, specialization):
                    print("Update failed. Please try again.")

            elif choice == 5:
                id = str(input("Enter the id of the carestaff that you want to remove: "))
                self.current_admin.remove_carestaffs([id])
            elif choice == 6:
                id = str(input("Enter the patients's patient ID: "))
                print("What do you want to get? ")
                print("1. Patient's information.")
                print("2. Patient's record.")
                choice = int(input("Enter your choice: "))
                self.current_admin.search_patient_information(id, choice)

            elif choice == 7:
                id = str(input("Enter the carestaff ID: "))
                num = self.current_admin.number_of_patients(id)
                if num is not None:
                    print(f"The number of patients for carestaff {id} is: {num}")
                else:
                    print("Carestaff not found. Please try again.")

            elif choice == 8:
                print("You are logging out...")
                admin_on = False
            input(Fore.WHITE + "\nPress Enter to continue...")

if __name__ == "__main__":
    admin_cli = AdminCLI()
    admin_cli.run()

