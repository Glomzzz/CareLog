#!/usr/bin/env python3
"""Nurse CLI - Command-line interface for nurse functionality in CareLog system."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import Fore, Style, init

from app.carestaff import Nurse
from app.datastore import DataStore

# Initialize colorama
init(autoreset=True)


class NurseCLI:
    """Command-line interface for nurse operations."""

    def __init__(self):
        self.current_nurse: Nurse | None = None
        self.running = True

    def display_banner(self):
        """Display welcome banner."""
        print("\n" + "=" * 60)
        print(Fore.CYAN + "         CareLog Nurse Management System")
        print("=" * 60 + "\n")

    def display_menu(self):
        """Display main menu options."""
        print(Fore.CYAN + "\n=== Main Menu ===")
        print("1. Login/Register")
        print("2. View My Patients")
        print("3. View/Update Vital Signs")
        print("4. Administer Medication")
        print("5. Manage Food Deliveries")
        print("6. Create Food Delivery")
        print("7. Coordinate Care")
        print("8. View Pending Tasks")
        print("9. View My Schedule")
        print("10. View Alerts")
        print("11. Generate Report")
        print("12. Logout")
        print("0. Exit")
        print(Fore.CYAN + "=" * 30)

    def register(self,id:str):
        """Register a new nurse."""
        print(Fore.CYAN + "\n=== Nurse Registration ===")
        name = input("Enter Full Name: ").strip()
        email = input("Enter Email: ").strip()
        password = input("Enter Password: ").strip()
        license_number = input("Enter License Number: ").strip()
        department = input("Enter Department: ").strip()
        qualifications = input("Enter Qualifications (comma-separated, optional): ").strip()

        qual_list = [q.strip() for q in qualifications.split(",")] if qualifications else []


        new_nurse = Nurse.register(
            name=name,
            carestaff_id=id,
            license_number=license_number,
            email=email,
            password=password,
            department=department,
            qualifications=qual_list,
        )

        if new_nurse:
            print(Fore.GREEN + f"✓ Registration successful! Your Nurse ID is {new_nurse.staff_id}")
            self.current_nurse = new_nurse
        else:
            print(Fore.RED + "✗ Registration failed. Please try again.")

    def login(self):
        """Handle nurse login."""
        print(Fore.CYAN + "\n=== Nurse Login ===")
        nurse_id = input("Enter Nurse ID: ").strip()

        self.current_nurse = Nurse.get_nurse_by_id(nurse_id)
        if not self.current_nurse:
            if (input(Fore.YELLOW + "? Nurse not found. Register? (y/n): ").lower() == "y"):
                self.register(nurse_id)
            return
        password = input("Enter Password: ").strip()

        # Attempt login
        credentials = {"email": self.current_nurse.email, "password": password}
        if self.current_nurse.login(credentials):
            print(Fore.GREEN + f"\n✓ Welcome, Nurse {self.current_nurse.name}!")
            print(Fore.GREEN + f"  License: {self.current_nurse.license_number}")
            if self.current_nurse.qualifications:
                print(Fore.GREEN + f"  Qualifications: {', '.join(self.current_nurse.qualifications)}")
        else:
            print(Fore.RED + "✗ Login failed. Please check credentials.")
            self.current_nurse = None

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

    def view_update_vitals(self):
        """View or update vital signs for a patient."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Vital Signs Management ===")
        patient_id = input("Enter Patient ID: ").strip()

        # Check if vitals exist
        vitals = self.current_nurse.get_patient_vitals(patient_id)
        
        if vitals:
            print(Fore.GREEN + f"\nCurrent Vital Signs for Patient {patient_id}:")
            print(f"  Temperature: {vitals.get('temperature', 'N/A')}°C")
            print(f"  Heart Rate: {vitals.get('heartRate', 'N/A')} bpm")
            print(f"  Blood Pressure: {vitals.get('bloodPressure', 'N/A')}")
            print(f"  Respiratory Rate: {vitals.get('respiratoryRate', 'N/A')} /min")
            print(f"  Oxygen Saturation: {vitals.get('oxygenSaturation', 'N/A')}%")
            print(f"  Last Updated: {vitals.get('measuredAt', 'N/A')}")
            
            # Check for anomalies
            anomalies = vitals.get('anomalies', [])
            if anomalies:
                print(Fore.YELLOW + "\n⚠ Anomalies Detected:")
                for anomaly in anomalies:
                    print(f"  - {anomaly}")

        # Option to update
        update = input("\nUpdate vital signs? (y/n): ").strip().lower()
        if update == 'y':
            print("\nEnter new vital signs (leave blank to skip):")
            temperature = input("Temperature (°C): ").strip()
            heart_rate = input("Heart Rate (bpm): ").strip()
            blood_pressure = input("Blood Pressure (e.g., 120/80): ").strip()
            respiratory_rate = input("Respiratory Rate (/min): ").strip()
            oxygen_saturation = input("Oxygen Saturation (%): ").strip()

            new_vitals = {}
            if temperature:
                new_vitals["temperature"] = float(temperature)
            if heart_rate:
                new_vitals["heart_rate"] = float(heart_rate)
            if blood_pressure:
                new_vitals["blood_pressure"] = blood_pressure
            if respiratory_rate:
                new_vitals["respiratory_rate"] = float(respiratory_rate)
            if oxygen_saturation:
                new_vitals["oxygen_saturation"] = float(oxygen_saturation)

            if new_vitals:
                if self.current_nurse.update_vital_signs(patient_id, new_vitals):
                    print(Fore.GREEN + f"✓ Vital signs updated for patient {patient_id}")
                    
                    # Check for new anomalies
                    updated_vitals = self.current_nurse.vital_signs.get(patient_id)
                    if updated_vitals:
                        anomalies = updated_vitals.detect_anomalies()
                        if anomalies:
                            print(Fore.RED + "\n⚠ WARNING: Anomalies detected!")
                            for anomaly in anomalies:
                                print(Fore.RED + f"  - {anomaly}")
                else:
                    print(Fore.RED + "✗ Failed to update vital signs")
            else:
                print(Fore.YELLOW + "No values entered. Update cancelled.")

    def administer_medication(self):
        """Record medication administration."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Administer Medication ===")
        patient_id = input("Enter Patient ID: ").strip()
        medication_name = input("Medication Name: ").strip()
        dosage = input("Dosage: ").strip()
        route = input("Route (e.g., oral, IV): ").strip()

        medication = {
            "name": medication_name,
            "dosage": dosage,
            "route": route,
            "time": datetime.now().isoformat(),
        }

        if self.current_nurse.mark_medication_administered(patient_id, medication):
            print(Fore.GREEN + f"✓ Medication '{medication_name}' administered to patient {patient_id}")
            print(Fore.GREEN + "  Task recorded successfully.")
        else:
            print(Fore.RED + "✗ Failed to record medication administration")

    def manage_food_deliveries(self):
        """Manage existing food deliveries."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Manage Food Deliveries ===")
        
        if not self.current_nurse.food_deliveries:
            print(Fore.YELLOW + "No food deliveries assigned.")
            return

        print("Current Food Deliveries:")
        for i, delivery in enumerate(self.current_nurse.food_deliveries, 1):
            status_color = {
                "pending": Fore.YELLOW,
                "delivered": Fore.GREEN,
                "cancelled": Fore.RED,
            }.get(delivery.status, Fore.WHITE)
            
            print(f"{i}. {status_color}[{delivery.status.upper()}] {delivery.delivery_id}")
            print(f"   Items: {delivery.food_items}")
            print(f"   Room: {delivery.room_number}")
            print(f"   Scheduled: {delivery.scheduled_time}")
            print()

        choice = input("Enter delivery number to manage (or 0 to skip): ").strip()
        if choice.isdigit() and 0 < int(choice) <= len(self.current_nurse.food_deliveries):
            delivery = self.current_nurse.food_deliveries[int(choice) - 1]
            
            print("\nActions:")
            print("1. Mark as Delivered")
            print("2. Cancel Delivery")
            print("3. Verify Allergies")
            
            action = input("Select action: ").strip()
            
            if action == "1":
                if self.current_nurse.manage_food_deliveries(delivery.delivery_id, "delivered"):
                    print(Fore.GREEN + f"✓ Delivery {delivery.delivery_id} marked as delivered")
            elif action == "2":
                if self.current_nurse.manage_food_deliveries(delivery.delivery_id, "cancel"):
                    print(Fore.GREEN + f"✓ Delivery {delivery.delivery_id} cancelled")
            elif action == "3":
                patient_id = input("Enter Patient ID to verify allergies: ").strip()
                # Load patient data
                data = DataStore.load_all()
                patient_data = next((p for p in data.get("patients", []) if p.get("patientID") == patient_id), None)
                
                if patient_data:
                    # TODO: Implement Patient class and allergy checking
                    pass
                    #     print(Fore.GREEN + "✓ No allergy conflicts detected")
                    # else:
                    #     print(Fore.RED + "✗ WARNING: Allergy conflict detected!")
                else:
                    print(Fore.RED + "✗ Patient not found")

    def create_food_delivery(self):
        """Create a new food delivery."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Create Food Delivery ===")
        patient_id = input("Enter Patient ID: ").strip()
        food_items = input("Food Items: ").strip()
        room_number = input("Room Number: ").strip()
        
        print("\nSchedule delivery:")
        hours_from_now = input("Hours from now (default 1): ").strip()
        hours = int(hours_from_now) if hours_from_now.isdigit() else 1
        scheduled_time = datetime.now() + timedelta(hours=hours)

        try:
            room_num = int(room_number)
            delivery = self.current_nurse.create_food_delivery(
                patient_id,
                food_items,
                room_num,
                scheduled_time,
            )
            print(Fore.GREEN + f"✓ Food delivery created: {delivery.delivery_id}")
            print(Fore.GREEN + f"  Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        except ValueError:
            print(Fore.RED + "✗ Invalid room number")

    def coordinate_care(self):
        """Coordinate care plan for a patient."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Coordinate Care ===")
        patient_id = input("Enter Patient ID: ").strip()
        
        print("\nCare Plan Type:")
        print("1. Observation")
        print("2. Nursing")
        print("3. Post-Op")
        print("4. Rehabilitation")
        
        choice = input("Select type (1-4): ").strip()
        type_map = {
            "1": "observation",
            "2": "nursing",
            "3": "post-op",
            "4": "rehabilitation",
        }
        care_type = type_map.get(choice, "nursing")
        
        notes = input("Care plan notes: ").strip()

        care_plan = {
            "type": care_type,
            "notes": notes,
            "created_by": self.current_nurse.staff_id,
            "created_at": datetime.now().isoformat(),
        }

        if self.current_nurse.coordinate_care(patient_id, care_plan):
            print(Fore.GREEN + f"✓ Care plan coordinated for patient {patient_id}")
            print(Fore.GREEN + f"  Type: {care_type}")
        else:
            print(Fore.RED + "✗ Failed to coordinate care")

    def view_pending_tasks(self):
        """View all pending tasks."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== Pending Tasks ===")
        pending = self.current_nurse.view_pending_tasks()

        if not pending:
            print(Fore.GREEN + "No pending tasks. All caught up!")
            return

        for i, task in enumerate(pending, 1):
            priority_color = {
                "high": Fore.RED,
                "normal": Fore.YELLOW,
                "low": Fore.WHITE,
            }.get(task.priority, Fore.WHITE)
            
            print(f"{i}. {priority_color}[{task.priority.upper()}] {task.title}")
            print(f"   Description: {task.description}")
            print(f"   Status: {task.status}")
            print(f"   Due: {task.due_date}")
            print()

        # Offer to complete a task
        choice = input("Mark task as complete? (Enter task number or 0 to skip): ").strip()
        if choice.isdigit() and 0 < int(choice) <= len(pending):
            task = pending[int(choice) - 1]
            if self.current_nurse.manage_tasks(task.task_id, "complete"):
                print(Fore.GREEN + f"✓ Task '{task.title}' marked as complete")
            else:
                print(Fore.RED + "✗ Failed to update task")

    def view_schedule(self):
        """View nurse's work schedule."""
        if not self.check_login():
            return

        print(Fore.CYAN + "\n=== My Schedule ===")
        schedules = self.current_nurse.view_schedules()

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
        alerts = self.current_nurse.view_patient_alerts()

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
            if self.current_nurse.handle_alert(alert.alert_id, action):
                print(Fore.GREEN + f"✓ Alert {action}d successfully")
            else:
                print(Fore.RED + "✗ Failed to handle alert")

    def generate_report(self):
        """Generate a report for the nurse's activities."""
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

        report = self.current_nurse.generate_reports(start_date, end_date)
        
        print(Fore.GREEN + "\n=== Activity Report ===")
        print(f"Nurse: {report['staff']}")
        print(f"Period: {report['period']}")
        print(f"Patients Managed: {report['patients_managed']}")
        print(f"Tasks Completed: {report['tasks_completed']}")
        
        # Additional stats
        print(f"\nFood Deliveries: {len(self.current_nurse.food_deliveries)}")
        print(f"Patients with Vitals Recorded: {len(self.current_nurse.vital_signs)}")
        print(f"Pending Tasks: {len(self.current_nurse.view_pending_tasks())}")
        print()

    def logout(self):
        """Logout current nurse."""
        if self.current_nurse:
            self.current_nurse.logout()
            print(Fore.GREEN + f"✓ Goodbye, Nurse {self.current_nurse.name}!")
            self.current_nurse = None
        else:
            print(Fore.YELLOW + "No active session.")

    def check_login(self):
        """Check if nurse is logged in."""
        if not self.current_nurse:
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
                    print(Fore.CYAN + "\nThank you for using CareLog Nurse System!")
                elif choice == "1":
                    self.login()
                elif choice == "2":
                    self.view_patients()
                elif choice == "3":
                    self.view_update_vitals()
                elif choice == "4":
                    self.administer_medication()
                elif choice == "5":
                    self.manage_food_deliveries()
                elif choice == "6":
                    self.create_food_delivery()
                elif choice == "7":
                    self.coordinate_care()
                elif choice == "8":
                    self.view_pending_tasks()
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
    """Entry point for nurse CLI."""
    cli = NurseCLI()
    cli.run()


if __name__ == "__main__":
    main()
