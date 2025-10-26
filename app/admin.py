import json

class Admin:

    """
    Admin class represents a user in the CareLog system.
    Stores personal information and login password to access the CareLog system.
    """

    def __init__ (self, name, adminID, phone, email, password):
        """
        Initialize a new Admin instance.

        name: Admin's name.
        email: Admin's email.
        phone: Admin's phone number.
        password: Admin's password to log in to the system.
        """
        self.name = name
        self.adminID = adminID
        self.phone = phone
        self.email = email
        self.password = password
    
    def add_new_patients(self, patients: list):
        """Admin's functional requirement 1: create patients."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Create patient dict for new patient(s)
        for patient in patients:
            data["patients"].append(patient)
        
        print("Patient(s) added successfully! ")
        print("The following patient(s) details were added: ")
        for patient in patients:
            for key, value in patient.items():
                print(f"{key}: {value}")
                
        # Save data for new patient(s) added
        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def update_patients_information(self, patientID, choice, information):
        """Admin's functional requirement 1: update patients information."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Choice 1: update patients' name
        # Choice 2: update patients' email
        # Choice 3: update patients' phone

        # Find the patient and update the information according to the inputted choice.
        patient_changed = None
        for patient in data["patients"]:
            if patient["patientID"] == patientID:
                if choice == 1:
                    patient["name"] = information
                    patient_changed = patient
                elif choice == 2:
                    patient["email"] = information
                    patient_changed = patient
                elif choice == 3:
                    patient["phone"] = information
                    patient_changed = patient

        # If not found, print error message.
        if patient_changed is None:
            print("Patient not found. Please try again. ")
        else:
            print(f"Patient information for patient ID {patient_changed['patientID']} successfully changed! ")
            print("The following are the updated details of the patient.")
            for key, value in patient_changed.items():
                print(f"{key}: {value}")

        # Save data after updated information.
        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    def remove_patients(self, patientID_list):
        """Admin's functional requirement 1: remove patients."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Find the patient(s) that wanted to be deleted and delete it.
        patients_deleted = []
        for patientID in patientID_list:
            for patient in data["patients"]:
                if patientID == patient["patientID"]:
                    data["patients"].remove(patient)
                    patients_deleted.append(patient)
        
        print("Patient(s) removed successfully! ")
        print("The following patient(s) details were removed: ")
        for patient in patients_deleted:
            for key, value in patient.items():
                print(f"{key}: {value}")

        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    def add_new_carestaffs(self, carestaffs):
        """Admin's functional requirement 1: create carestaffs."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Create carestaff dict for new carestaff(s)
        for carestaff in carestaffs:
            data["carestaffs"].append(carestaff)
        
        print("Carestaff(s) added successfully! ")
        print("The following carestaff(s) details were added: ")
        for carestaff in carestaffs:
            for key, value in carestaff.items():
                print(f"{key}: {value}")
                
        # Save data for new carestaff(s) added
        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    def update_carestaffs_information(self, staffID, department, specialization):
        """Admin's functional requirement 1: update carestaffs information."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)


        # Find the carestaff and update the information according to the input.
        carestaff_changed = None
        for carestaff in data["carestaffs"]:
            if carestaff["staffID"] == staffID:
                carestaff["department"] = department
                carestaff["specialization"] = specialization
                carestaff_changed = carestaff

        # If not found, print error message.
        if carestaff_changed is None:
            print("Carestaff not found. Please try again. ")
        else:
            print(f"Carestaff information for carestaff ID {carestaff_changed['staffID']} successfully changed! ")
            print("The following are the updated details of the carestaff.")
            for key, value in carestaff_changed.items():
                print(f"{key}: {value}")

        # Save data after updated information.
        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    def remove_carestaffs(self, staffID_list):
        """Admin's functional requirement 1: remove patients."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Find the carestaff(s) that wanted to be deleted and delete it.
        carestaffs_deleted = []
        for staffID in staffID_list:
            for carestaff in data["carestaffs"]:
                if staffID == carestaff["staffID"]:
                    data["carestaffs"].remove(carestaff)
                    carestaffs_deleted.append(carestaff)
        
        print("Carestaff(s) removed successfully! ")
        print("The following carestaff(s) details were removed: ")
        for carestaff in carestaffs_deleted:
            for key, value in carestaff.items():
                print(f"{key}: {value}")

        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    
    def search_patient_information(self, patientID):
        """Admin's functional requirement 2: search for the patient personal information."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        list_of_patients = data["patients"]

        # Find if the input patient ID exists.
        patient_found = False
        for patient in list_of_patients:
            if patient["patientID"] == patientID:
                patient_found = patient

        if patient_found:
            print("Patient found! The following are the patient's information found:")
            for key, value in patient_found.items():
                print(f"{key}: {value}")
        else:
            print("Patient not found! Please try again.")
    
    def number_of_patients(self, staffID):
        """Admin's functional requirement 3: get the number of patients that a care staff has."""
        # Load data from carelog.json file
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Return the number of patients that a care staff has.
        for carestaff in data["carestaffs"]:
            if carestaff["staffID"] == staffID:
                return len(carestaff["assignedPatients"])