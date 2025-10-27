#!/usr/bin/env python3
"""Top-level CLI to choose Patient, Nurse, Doctor, or Admin interfaces."""

from pathlib import Path
import sys

# Ensure repo root is on path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import Fore, init

from cli.doctor_cli import DoctorCLI
from cli.nurse_cli import NurseCLI
from cli.admin_cli import AdminCLI
from cli.patient_cli import PatientCli

init(autoreset=True)


def display_banner():
    print("\n" + "=" * 60)
    print(Fore.CYAN + "             CareLog Unified CLI")
    print("=" * 60 + "\n")


def display_menu():
    print(Fore.CYAN + "\nSelect role to continue:")
    print("1. Patient")
    print("2. Nurse")
    print("3. Doctor")
    print("4. Admin")
    print("0. Exit")


def main():
    display_banner()
    while True:
        display_menu()
        choice = input(Fore.WHITE + "Enter choice: ").strip()
        if choice == "0":
            print(Fore.CYAN + "Goodbye!")
            break
        elif choice == "1":
            # Delegate to existing patient flow (main.py)
            try:
                PatientCli().run()
            except Exception as e:
                print(Fore.RED + f"Error launching patient UI: {e}")
        elif choice == "2":
            NurseCLI().run()
        elif choice == "3":
            DoctorCLI().run()
        elif choice == "4":
            AdminCLI().run()
        else:
            print(Fore.YELLOW + "Invalid choice, try again.")
        input(Fore.WHITE + "\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
