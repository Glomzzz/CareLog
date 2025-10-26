#!/usr/bin/env python3
"""Doctor CLI - Command-line interface for doctor functionality in CareLog system."""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import Fore, init

from app.carestaff import Doctor
from app.datastore import DataStore

# Initialize colorama
init(autoreset=True)


class DoctorCLI:
    """Command-line interface for doctor operations."""

    def __init__(self):
        self.current_doctor: Doctor | None = None
        self.running = True

    def display_banner(self):
        """Display welcome banner."""
        print("\n" + "=" * 60)
        print(Fore.CYAN + "         CareLog Doctor Management System")
        print("=" * 60 + "\n")

    def display_menu(self):
        """Display main menu options."""
        print(Fore.CYAN + "\n=== Main Menu ===")
        print("1. Login/Register")
        print("2. View My Patients")
        print("3. View Medical Records")
        print("4. Update Medical Details")
        print("5. Prescribe Medication")
        print("6. Approve Treatment Plan")
        print("7. Escalate to Specialist")
        print("8. Manage Appointments")
        print("9. View My Schedule")
        print("10. View Alerts")
        print("11. Generate Report")
        print("12. Logout")
        print("0. Exit")
        print(Fore.CYAN + "=" * 30)

    def register(self,id:str):
        """Register a new doctor."""
        print(Fore.CYAN + "\n=== Doctor Registration ===")
        name = input("Enter Full Name: ").strip()
        email = input("Enter Email: ").strip()
        password = input("Enter Password: ").strip()
        license_number = input("Enter License Number: ").strip()
        department = input("Enter Department: ").strip()

        new_doctor = Doctor.register(
            name,
            id,
            license_number,
            email,
            password,
            department=department,
        )

        if new_doctor:
            print(Fore.GREEN + f"✓ Registration successful! Your Doctor ID is {new_doctor.staff_id}")
            self.current_doctor = new_doctor
        else:
            print(Fore.RED + "✗ Registration failed. Please try again.")

    def login(self):
        """Handle doctor login."""
        print(Fore.CYAN + "\n=== Doctor Login ===")
        doctor_id = input("Enter Doctor ID: ").strip()
        

        self.current_doctor = Doctor.get_doctor_by_id(doctor_id)
        if not self.current_doctor:
            if (input(Fore.YELLOW + "? Doctor not found. Register? (y/n): ").lower() == "y"):
                self.register(doctor_id)
            return
        password = input("Enter Password: ").strip()

        # Attempt login
        credentials = {"email": self.current_doctor.email, "password": password}
        if self.current_doctor.login(credentials):
            print(Fore.GREEN + f"\n✓ Welcome, Dr. {self.current_doctor.name}!")
            print(Fore.GREEN + f"  Department: {self.current_doctor.department}")
            print(Fore.GREEN + f"  License: {self.current_doctor.license_number}")
        else:
            print(Fore.RED + "✗ Login failed. Please check credentials.")
            self.current_doctor = None

    def view_patients(self):
        """View all assigned patients."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== My Assigned Patients ===")
        data = DataStore.load_all()
        patients = data.get("patients", [])

        if not patients:
            print(Fore.YELLOW + "No patients found in system.")
            return

        for i, patient in enumerate(patients, 1):
            risk_marker = Fore.RED + " [HIGH RISK]" if patient.get("high_risk") else ""
            print(f"{i}. {Fore.WHITE}ID: {patient.get('patientID')} | "
                  f"Name: {patient.get('name')} | "
                  f"Disease: {patient.get('disease', 'N/A')}{risk_marker}")

    def view_medical_records(self):
        """View medical records for a specific patient."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== View Medical Records ===")
        patient_id = input("Enter Patient ID: ").strip()

        records = self.current_doctor.view_medical_records(patient_id)
        if not records:
            print(Fore.YELLOW + f"No medical records found for patient {patient_id}.")
            return

        print(Fore.GREEN + f"\nMedical Records for Patient {patient_id}:")
        print(f"  Diagnosis: {records.get('sickness_name', 'N/A')}")
        print(f"  Department: {records.get('department', 'N/A')}")
        print(f"  Description: {records.get('description', 'N/A')}")
        print(f"  Medications: {', '.join(records.get('medications', [])) or 'None'}")
        print(f"  Status: {records.get('status', 'N/A')}")
        print(f"  Last Updated: {records.get('updatedAt', 'N/A')}")

    def update_medical_details(self):
        """Update medical details for a patient."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Update Medical Details ===")
        patient_id = input("Enter Patient ID: ").strip()
        
        print("\nEnter new information (leave blank to skip):")
        sickness_name = input("Diagnosis/Sickness Name: ").strip()
        description = input("Description: ").strip()
        medications = input("Medications (comma-separated): ").strip()
        department = input("Department: ").strip()

        medical_info = {}
        if sickness_name:
            medical_info["sickness_name"] = sickness_name
        if description:
            medical_info["description"] = description
        if medications:
            medical_info["medications"] = [m.strip() for m in medications.split(",")]
        if department:
            medical_info["department"] = department

        if not medical_info:
            print(Fore.YELLOW + "No information provided. Update cancelled.")
            return

        if self.current_doctor.update_medical_details( patient_id, medical_info):
            print(Fore.GREEN + f"✓ Medical details updated for patient {patient_id}")
        else:
            print(Fore.RED + "✗ Failed to update medical details")

    def prescribe_medication(self):
        """Prescribe medication to a patient."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Prescribe Medication ===")
        patient_id = input("Enter Patient ID: ").strip()
        medication_name = input("Medication Name: ").strip()
        dosage = input("Dosage (optional): ").strip()
        frequency = input("Frequency (optional): ").strip()

        medication = {"name": medication_name}
        if dosage:
            medication["dosage"] = dosage
        if frequency:
            medication["frequency"] = frequency

        if self.current_doctor.prescribe_medication( patient_id, medication):
            print(Fore.GREEN + f"✓ Prescribed {medication_name} to patient {patient_id}")
        else:
            print(Fore.RED + f"✗ Failed to prescribe. Check if patient {patient_id} has medical records.")

    def approve_treatment_plan(self):
        """Approve a treatment plan for a patient."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Approve Treatment Plan ===")
        patient_id = input("Enter Patient ID: ").strip()
        
        print("\nTreatment Status Options:")
        print("1. Approved")
        print("2. Pending Review")
        print("3. Rejected")
        choice = input("Select status (1-3): ").strip()

        status_map = {"1": "approved", "2": "pending", "3": "rejected"}
        status = status_map.get(choice, "pending")

        if self.current_doctor.approve_treatment_plans( patient_id, {"status": status}):
            print(Fore.GREEN + f"✓ Treatment plan {status} for patient {patient_id}")
        else:
            print(Fore.RED + f"✗ Failed to update treatment plan. Check if patient {patient_id} has medical records.")

    def escalate_to_specialist(self):
        """Escalate a patient case to a specialist."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Escalate to Specialist ===")
        patient_id = input("Enter Patient ID: ").strip()
        specialist_type = input("Specialist Type (e.g., Cardiology, Neurology): ").strip()

        if self.current_doctor.escalate_to_specialist( patient_id, specialist_type):
            print(Fore.GREEN + f"✓ Case escalated to {specialist_type} for patient {patient_id}")
            print(Fore.YELLOW + "  Alert created and notification sent.")
        else:
            print(Fore.RED + "✗ Failed to escalate case")

    def manage_appointments(self):
        """Manage doctor appointments."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Manage Appointments ===")
        print("Current Appointments:")
        
        if not self.current_doctor.appointment_list:
            print(Fore.YELLOW + "No appointments scheduled.")
        else:
            for i, appt_id in enumerate(self.current_doctor.appointment_list, 1):
                print(f"{i}. {appt_id}")

        print("\nActions:")
        print("1. Add Appointment")
        print("2. Approve Appointment")
        print("3. Cancel Appointment")
        print("0. Back")
        
        choice = input("\nSelect action: ").strip()

        if choice == "1":
            appt_id = input("Enter Appointment ID: ").strip()
            if self.current_doctor.add_appointment( appt_id):
                print(Fore.GREEN + f"✓ Appointment {appt_id} added")
            else:
                print(Fore.RED + "✗ Appointment already exists")
        elif choice == "2":
            appt_id = input("Enter Appointment ID to approve: ").strip()
            if self.current_doctor.manage_appointments( appt_id, "approve"):
                print(Fore.GREEN + f"✓ Appointment {appt_id} approved")
            else:
                print(Fore.RED + "✗ Appointment not found")
        elif choice == "3":
            appt_id = input("Enter Appointment ID to cancel: ").strip()
            if self.current_doctor.manage_appointments( appt_id, "cancel"):
                print(Fore.GREEN + f"✓ Appointment {appt_id} cancelled")
            else:
                print(Fore.RED + "✗ Appointment not found")

    def view_schedule(self):
        """View doctor's work schedule."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== My Schedule ===")
        schedules = self.current_doctor.view_schedules()

        if not schedules:
            print(Fore.YELLOW + "No scheduled activities.")
            return

        for i, schedule in enumerate(schedules, 1):
            print(f"{i}. {Fore.WHITE}Task: {schedule.task}")
            print(f"   Date: {schedule.date}")
            print(f"   Purpose: {schedule.purpose}")
            print(f"   Priority: {schedule.priority}")
            if schedule.location:
                print(f"   Location: {schedule.location}")
            print()

    def view_alerts(self):
        """View all alerts."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== My Alerts ===")
        alerts = self.current_doctor.view_patient_alerts()

        if not alerts:
            print(Fore.YELLOW + "No active alerts.")
            return

        for i, alert in enumerate(alerts, 1):
            severity_color = {
                "high": Fore.RED,
                "medium": Fore.YELLOW,
                "low": Fore.WHITE,
            }.get(alert.severity, Fore.WHITE)

            print(f"{i}. {severity_color}[{alert.severity.upper()}] {alert.message}")
            print(f"   Type: {alert.type} | Priority: {alert.calculate_priority()}")
            print(f"   Acknowledged: {'Yes' if alert.acknowledged_at else 'No'}")
            print(f"   Resolved: {'Yes' if alert.resolved_at else 'No'}")
            print()

        # Offer to handle alerts
        choice = input("\nHandle an alert? (Enter alert number or 0 to skip): ").strip()
        if choice.isdigit() and 0 < int(choice) <= len(alerts):
            alert = alerts[int(choice) - 1]
            action = input("Action (acknowledge/resolve): ").strip().lower()
            if self.current_doctor.handle_alert(alert.alert_id, action):
                print(Fore.GREEN + f"✓ Alert {action}d successfully")
            else:
                print(Fore.RED + "✗ Failed to handle alert")

    def generate_report(self):
        """Generate a report for the doctor's activities."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Generate Report ===")
        print("Enter report period:")
        start_date_str = input("Start date (YYYY-MM-DD): ").strip()
        end_date_str = input("End date (YYYY-MM-DD): ").strip()

        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            print(Fore.RED + "✗ Invalid date format. Use YYYY-MM-DD.")
            return

        report = self.current_doctor.generate_reports(start_date, end_date)
        
        print(Fore.GREEN + "\n=== Activity Report ===")
        print(f"Doctor: {report['staff']}")
        print(f"Period: {report['period']}")
        print(f"Patients Managed: {report['patients_managed']}")
        print(f"Tasks Completed: {report['tasks_completed']}")
        print()

        # Generate treatment reports for patients
        patient_id = input("Generate treatment report for patient ID (or press Enter to skip): ").strip()
        if patient_id:
            treatment_report = self.current_doctor.generate_treatment_report(patient_id)
            if "error" in treatment_report:
                print(Fore.RED + f"✗ {treatment_report['error']}")
            else:
                print(Fore.GREEN + "\n=== Treatment Report ===")
                for key, value in treatment_report.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")

    def logout(self):
        """Logout current doctor."""
        if self.current_doctor:
            self.current_doctor.logout()
            print(Fore.GREEN + f"✓ Goodbye, Dr. {self.current_doctor.name}!")
            self.current_doctor = None
        else:
            print(Fore.YELLOW + "No active session.")

    def check_login(self):
        """Check if doctor is logged in."""
        if not self.current_doctor:
            print(Fore.RED + "✗ Please login first.")
            return False
        return True

    def run(self):
        """Main application loop."""
        self.display_banner()

        while self.running:
            self.display_menu()
            choice = input(Fore.WHITE + "\nEnter your choice: ").strip()

            try:
                if choice == "0":
                    self.running = False
                    print(Fore.CYAN + "\nThank you for using CareLog Doctor System!")
                elif choice == "1":
                    self.login()
                elif choice == "2":
                    self.view_patients()
                elif choice == "3":
                    self.view_medical_records()
                elif choice == "4":
                    self.update_medical_details()
                elif choice == "5":
                    self.prescribe_medication()
                elif choice == "6":
                    self.approve_treatment_plan()
                elif choice == "7":
                    self.escalate_to_specialist()
                elif choice == "8":
                    self.manage_appointments()
                elif choice == "9":
                    self.view_schedule()
                elif choice == "10":
                    self.view_alerts()
                elif choice == "11":
                    self.generate_report()
                elif choice == "12":
                    self.logout()
                else:
                    print(Fore.RED + "✗ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nOperation cancelled by user.")
            except Exception as e:
                print(Fore.RED + f"✗ Error: {str(e)}")
            input(Fore.WHITE + "\nPress Enter to continue...")

        print(Fore.CYAN + "Exiting...\n")


def main():
    """Entry point for doctor CLI."""
    cli = DoctorCLI()
    cli.run()


if __name__ == "__main__":
    main()
