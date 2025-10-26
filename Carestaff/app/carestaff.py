import json
from app.note import Note
from app.schedule import Schedule
from colorama import Fore, Style

class CareStaff:
    def __init__(self, name, carestaffID):
        self.name = name
        self.carestaffID = carestaffID

    def _load_data(self):
        with open("data/carelog.json", "r") as f:
            return json.load(f)

    def _save_data(self, data):
        with open("data/carelog.json", "w") as f:
            json.dump(data, f, indent=4)

    def add_note(self, patientID, content):
        data = self._load_data()
        note = Note(patientID, self.carestaffID, content)
        data["notes"].append(note.to_dict())
        self._save_data(data)
        print(Fore.GREEN + "Note added successfully!" + Style.RESET_ALL)

    def update_disease(self, patientID, new_disease):
        data = self._load_data()
        for p in data["patients"]:
            if p["patientID"] == patientID:
                p["disease"] = new_disease
                self._save_data(data)
                print(Fore.GREEN + f"Disease updated for {p['name']}!" + Style.RESET_ALL)
                return
        print(Fore.RED + "Patient not found." + Style.RESET_ALL)

    def search_patient(self, keyword):
        data = self._load_data()
        print(Fore.CYAN + "Search results:" + Style.RESET_ALL)
        for p in data["patients"]:
            if keyword.lower() in p["name"].lower() or keyword.lower() in p["patientID"].lower():
                risk_color = Fore.YELLOW if p["high_risk"] else Fore.WHITE
                print(risk_color + f"ID: {p['patientID']} | Name: {p['name']} | Disease: {p['disease']}" + Style.RESET_ALL)

    def view_notes(self, patientID):
        data = self._load_data()
        found = [n for n in data["notes"] if n["patientID"] == patientID]
        if not found:
            print(Fore.RED + "No notes found for this patient." + Style.RESET_ALL)
        else:
            print(Fore.CYAN + f"Notes for patient {patientID}:" + Style.RESET_ALL)
            for n in found:
                print(f"- ({n['timestamp']}) {n['content']} (by {n['author']})")

    def add_schedule(self, task, date):
        data = self._load_data()
        schedule = Schedule(self.carestaffID, task, date)
        data["schedules"].append(schedule.to_dict())
        self._save_data(data)
        print(Fore.GREEN + "Schedule added successfully!" + Style.RESET_ALL)

    def toggle_high_risk(self, patientID):
        data = self._load_data()
        for p in data["patients"]:
            if p["patientID"] == patientID:
                p["high_risk"] = not p["high_risk"]
                self._save_data(data)
                
                if p["high_risk"]:
                    print(Fore.YELLOW + f"Patient {p['name']} is now marked HIGH RISK!" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"Patient {p['name']} is no longer high risk." + Style.RESET_ALL)
                return
        
        print(Fore.RED + "Patient not found." + Style.RESET_ALL)

