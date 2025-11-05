# CareLog CLI Tools

This directory contains command-line interface (CLI) tools for the CareLog hospital management system.

## Available CLIs

### Doctor CLI (`doctor_cli.py`)

A comprehensive interface for doctors to manage patients and medical records.

**Features:**
- Login with credentials
- View assigned patients
- View and update medical records
- Prescribe medications
- Approve treatment plans
- Escalate cases to specialists
- Manage appointments
- View work schedule
- Handle alerts
- Generate activity and treatment reports

**Usage:**
```bash
python cli/doctor_cli.py
```

Or if executable:
```bash
./cli/doctor_cli.py
```

### Nurse CLI (`nurse_cli.py`)

A comprehensive interface for nurses to manage patient care and daily tasks.

**Features:**
- Login with credentials
- View assigned patients
- View and update vital signs (temperature, heart rate, blood pressure, etc.)
- Administer medications
- Manage food deliveries
- Create food deliveries
- Coordinate care plans
- View pending tasks
- View work schedule
- Handle alerts
- Generate activity reports

**Usage:**
```bash
python cli/nurse_cli.py
```

Or if executable:
```bash
./cli/nurse_cli.py
```

## Sample Workflow

### Doctor Workflow Example
1. Login with doctor credentials
2. View patients to see all assigned cases
3. Select a patient and view their medical records
4. Update medical details or prescribe medication
5. Approve treatment plans
6. If needed, escalate to a specialist
7. Check alerts and handle any urgent matters
8. Generate reports for documentation

### Nurse Workflow Example
1. Login with nurse credentials
2. View patients to see all assigned cases
3. Update vital signs for patients during rounds
4. Administer scheduled medications
5. Create or manage food deliveries
6. Check pending tasks and mark them complete
7. Handle any alerts
8. Generate activity reports for shift handover

## Features Overview

### Common Features (Both CLIs)
- Secure login system
- Patient management
- Alert handling (acknowledge/resolve)
- Schedule viewing
- Report generation
- Session management (logout)

### Doctor-Specific Features
- Medical record management
- Medication prescription
- Treatment plan approval
- Case escalation to specialists
- Appointment management
- Treatment report generation

### Nurse-Specific Features
- Vital signs monitoring with anomaly detection
- Medication administration tracking
- Food delivery management
- Care plan coordination
- Task completion tracking
- Patient vital statistics

## Data Storage

All CLIs interact with the centralized DataStore located at `data/carelog_data.json`. Changes made through the CLI are persisted to this file.

## Color-Coded Interface

Both CLIs use color-coding for better readability:
- **Green**: Success messages and normal status
- **Yellow**: Warnings and pending items
- **Red**: Errors, high-risk patients, and urgent alerts
- **Cyan**: Headers and informational text

## Requirements

- Python 3.13+
- colorama (for colored terminal output)
- All dependencies listed in `requirements.txt`

## Navigation

Both CLIs use menu-driven navigation:
- Enter the number corresponding to your choice
- Use `0` to exit or return to previous menu
- Use `12` to logout from your session
- Press `Ctrl+C` to cancel any operation

## Error Handling

Both CLIs include comprehensive error handling:
- Invalid input validation
- File I/O error management
- Graceful keyboard interrupt handling
- User-friendly error messages

## Testing

The CLI functionality is backed by comprehensive unit tests in `tests/test_carestaff.py`:
- 46 test cases covering all CareStaff, Doctor, and Nurse features
- Integration tests for doctor-nurse collaboration
- Edge case testing for all operations

Run tests with:
```bash
python -m pytest tests/test_carestaff.py -v
```

## Development

To add new features:
1. Update the corresponding class in `app/carestaff.py`
2. Add unit tests in `tests/test_carestaff.py`
3. Update the CLI menu and add handler method
4. Test thoroughly before deployment

## Notes

- Always login before performing any operations
- The system validates all inputs before processing
- Logout when done to properly close the session
- Medical data is sensitive - handle with care
