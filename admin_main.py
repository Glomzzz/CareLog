import json
from users.admin import Admin
#from users.patient import Patient

if __name__ == "__main__":

    print("[ADMIN'S CARELOG PAGE] Welcome!")
    adminid = str(input("Please input your admin ID here: "))
    password = str(input("Please input your password here: "))

    with open("data/carelog.json", "r") as f:
        data = json.load(f)
    
    list_of_admins = data["admins"]
    admin_login_succeed = False
    for admin in list_of_admins:
        if admin["adminID"] == adminid and admin["password"] == password:
            admin_login_succeed = True
            admin_logged_in = admin
    
    if not admin_login_succeed:
        print("Admin not found or password incorrect. Please reload and try again. ")
    else:
        print(f"Login successful! Welcome back {admin_logged_in['name']}! ")
        admin_on = True
        current_admin = Admin(admin_logged_in['name'], admin_logged_in['adminID'], admin_logged_in['phone'], admin_logged_in['email'], admin_logged_in['password'])
        while admin_on:
            print("[ADMIN'S MAIN MENU]")
            print("1. Add patient(s).")
            print("2. Update patient's information.")
            print("3. Remove patient(s).")
            print("4. Add carestaff(s).")
            print("5. Update carestaff's information.")
            print("6. Remove carestaff(s).")
            print("7. Get patient's information or record.")
            print("8. Get the number of patients for all the carestaffs has.")
            print("9. Searching file of patients and carestaffs by keywords.")
            print("10. Log out.")

            choice = int(input("Enter your choice: "))

            if choice == 1:
                number_of_patients = int(input("Enter the number of patients that you want to add: "))

                new_patients_list = []
                for i in range(number_of_patients):
                    print(f"You are entering details for patient number {i + 1}.")
                    adminID = str(input("Enter the patient ID assigned to the new patient: "))
                    name = str(input("Enter patient's name: "))
                    email = str(input("Enter patient's email: "))
                    phone = str(input("Enter patient's phone: "))
                    print("The default password hash for the patient is [abcd1234] - patient can change it themselves afterwards.")
                    # Create new patient, add it into list of patients
                current_admin.add_new_patients(new_patients_list)
            
            elif choice == 2:
                patientID = str(input("Enter the patient ID of the patient's information that you want to change: "))
                print("Which information do you want to change? ")
                print("1. Patient's name.")
                print("2. Patient's email.")
                print("3. Patient's phone.")
                choice = int(input("Enter your choice: "))
                information = str(input("What do you want to change it to: "))

                current_admin.update_patients_information(patientID, choice, information)

            elif choice == 3:
                number_of_patients = int(input("Enter the number of patients that you want to remove: "))

                patientID_list = []
                print("Please enter the patient ID of the patient that you want to delete - one by one.")
                for i in range(number_of_patients):
                    patientID = str(input(f"{i+1}: "))
                    patientID_list.append(patientID)
                
                current_admin.remove_patients(patientID_list)
            
            elif choice == 4:
                pass

            elif choice == 5:
                pass

            elif choice == 6:
                pass

            elif choice == 7:
                patientID = str(input("Enter the patients's patient ID: "))
                print("What do you want to get? ")
                print("1. Patient's information.")
                print("2. Patient's record.")
                choice = int(input("Enter your choice: "))
                current_admin.search_patient_information(patientID, choice)

            elif choice == 8:
                pass

            elif choice == 9:
                pass

            elif choice == 10:
                print("You are logging out...")
                admin_on = False




