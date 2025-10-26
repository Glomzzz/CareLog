import json

class Admin:

    def __init__ (self, name, adminID, phone, email, password):
        self.name = name
        self.adminID = adminID
        self.phone = phone
        self.email = email
        self.password = password
    
    def add_new_patients(self, patients: list):
        """Admin's functional requirement 1: create patients."""
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        patients_added = []
        for patient in patients:
            new_patient = {
                "patientID": patient.id,
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "password_hash": patient.password_hash
            }
            data["patients"].append(new_patient)
            patients_added.append(new_patient)
        
        print("Patient(s) added successfully! ")
        print("The following patient(s) details were added: ")
        for patient in patients_added:
            for key, value in patient.items():
                print(f"{key}: {value}")

        with open("data/carelog.json", "w") as f:
            json.dump(data, f)
    
    def update_patients_information(self, patientID, choice, information):
        """Admin's functional requirement 1: update patients information."""
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        # Choice 1: update patients' name
        # Choice 2: update patients' email
        # Choice 3: update patients' phone

        patient_changed = None
        for patient in data["patients"]:
            if patient.id == patientID:
                if choice == 1:
                    patient["name"] = information
                    patient_changed = patient
                elif choice == 2:
                    patient["email"] = information
                    patient_changed = patient
                elif choice == 3:
                    patient["phone"] = information
                    patient_changed = patient

        if patient_changed is None:
            print("Patient not found. Please try again. ")
        else:
            print(f"Patient information for patient ID {patient_changed.id} successfully changed! ")
            print("The following are the updated details of the patient.")
            for key, value in patient_changed.items():
                print(f"{key}: {value}")

        with open("data/carelog.json", "w") as f:
            json.dump(data, f)

    def remove_patients(self, patientID_list):
        """Admin's functional requirement 1: remove patients."""
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        patients_deleted = []
        for patientID in patientID_list:
            for patient in data["patients"]:
                if patientID == patient.id:
                    data["patients"].remove(patient)
                    patients_deleted.append(patient)
        
        print("Patient(s) removed successfully! ")
        print("The following patient(s) details were removed: ")
        for patient in patients_deleted:
            for key, value in patient.items():
                print(f"{key}: {value}")

        with open("data/carelog.json", "w") as f:
            json.dump(data, f)

    def add_new_carestaffs(self):
        """Admin's functional requirement 1: create carestaffs."""
        pass

    def update_carestaffs_information(self):
        """Admin's functional requirement 1: update carestaffs information."""
        pass

    def remove_carestaffs(self):
        """Admin's functional requirement 1: remove carestaffs."""
        pass
    
    def search_patient_information(self, patientID, choice):
        """Admin's functional requirement 2: search for the patient information or records."""
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        list_of_patients = data["patients"]

        patient_found = False
        for patient in list_of_patients:
            if patient["patientID"] == patientID:
                patient_found = patient

        # Choice 1: output patient's information.
        # Choice 2: output patient's record.

        if patient_found:
            if choice == 1:
                print("Patient found! The following are the patient's information found:")
                for key, value in patient_found.items():
                    print(f"{key}: {value}")
            elif choice == 2:
                pass

    def get_carestaff_assigned(self, carestaffID):
        """Admin's functional requirement 3: get the number of patients that a care staff has."""
        with open("data/carelog.json", "r") as f:
            data = json.load(f)

        list_of_carestaffs = data["carestaffs"]
        for carestaff in list_of_carestaffs:
            pass
        pass

    def search_patient_or_carestaff(self):
        """Admin's functional requirement 4: searching file of patients and carestaffs by keywords."""
        pass