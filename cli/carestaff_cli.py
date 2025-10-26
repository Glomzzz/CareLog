import json
from Carestaff.app.carestaff import CareStaff

if __name__ == "__main__":
    print("[CARE STAFF LOGIN PAGE]")
    
    with open("data/carelog.json", "r") as f:
        data = json.load(f)

    while True:
        carestaff_id = input("Enter your CareStaff ID (or q to quit): ")
        if carestaff_id.lower() == "q":
            print("Goodbye!")
            exit()

        password = input("Enter your password: ")

        carestaff = None
        for cs in data["carestaffs"]:
            if cs["carestaffID"] == carestaff_id:
                if cs["password"] == password:
                    carestaff = CareStaff(cs["name"], cs["carestaffID"])
                    print(f"Welcome back, {cs['name']}!")
                    break
                else:
                    print("Incorrect password. Try again.\n")
                    carestaff = "invalid"   # flag để chỉ đúng ID nhưng sai password
                    break
        
        if carestaff == "invalid":
            continue

        if carestaff is None:
            print("CareStaff ID not found. Please try again.\n")
            continue

        break

    while True:
        print("\n[CARE STAFF MENU]")
        print("1. Record patient note")
        print("2. Update patient disease")
        print("3. Search patient")
        print("4. View patient notes")
        print("5. Add schedule/reminder")
        print("6. Toggle high-risk status")
        print("7. Log out")

        choice = input("Enter your choice: ")

        if choice == "1":
            pid = input("Enter patient ID: ")
            content = input("Enter note content: ")
            carestaff.add_note(pid, content)

        elif choice == "2":
            pid = input("Enter patient ID: ")
            new_disease = input("Enter updated disease: ")
            carestaff.update_disease(pid, new_disease)

        elif choice == "3":
            keyword = input("Enter keyword (name or ID): ")
            carestaff.search_patient(keyword)

        elif choice == "4":
            pid = input("Enter patient ID: ")
            carestaff.view_notes(pid)

        elif choice == "5":
            task = input("Enter schedule task: ")
            date = input("Enter schedule date (YYYY-MM-DD): ")
            carestaff.add_schedule(task, date)

        elif choice == "6":
            pid = input("Enter patient ID: ")
            carestaff.toggle_high_risk(pid)

        elif choice == "7":
            print("Logging out... Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")