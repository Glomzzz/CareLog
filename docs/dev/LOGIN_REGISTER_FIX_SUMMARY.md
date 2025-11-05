# Doctor and Nurse Login & Registration Fix Summary

## Issues Fixed

### 1. Collection Name Inconsistency
**Problem:** Registration saved to `"carestaff"` but retrieval looked in `"carestaffs"`
**Solution:** Updated all methods to use consistent collection name `"carestaffs"`

### 2. Missing Password in Serialization
**Problem:** `CareStaff.to_dict()` didn't include the password field, causing login to fail after retrieval
**Solution:** Added `"password": self.password` to the `to_dict()` method

### 3. Incorrect Method Signatures in register()
**Problem:** Doctor and Nurse `__init__` require first 3 args as positional, but register was passing all as keyword args
**Solution:** Changed register methods to pass `name, carestaff_id, license_number` as positional args

### 4. Wrong Retrieval Methods in CLIs
**Problem:** CLIs used generic `get_carestaff_by_id()` which didn't properly cast to Doctor/Nurse types
**Solution:** Created specific `get_doctor_by_id()` and `get_nurse_by_id()` class methods

### 5. CLI Registration Flow Issues
**Problem:** 
- `doctor_cli.py` line 69 called `new_doctor.register()` on an already-registered Doctor instance
- `nurse_cli.py` line 89 called `get_carestaff_by_id()` twice
**Solution:** 
- Removed redundant `.register()` call and set `self.current_doctor = new_doctor` directly
- Removed duplicate retrieval call in nurse CLI
- Fixed prompt text (changed "Doctor ID" to "Nurse ID" in nurse CLI)

## Changes Made

### app/carestaff.py

#### CareStaff class:
- **to_dict()**: Added `"password": self.password` to serialization
- **get_carestaff_by_id()**: Changed collection from `"carestaff"` to `"carestaffs"`

#### Doctor class:
- **register()**: 
  - Fixed argument passing (positional for first 3 args)
  - Changed from `DataStore.load_all() / save_all()` to `DataStore.upsert()`
  - Changed collection to `"carestaffs"`
  - Renamed variable from `password` to `hashed_password` for clarity
- **get_doctor_by_id()**: New method to retrieve and cast Doctor instances with role validation

#### Nurse class:
- **register()**: 
  - Fixed argument passing (positional for first 3 args)
  - Changed from `DataStore.load_all() / save_all()` to `DataStore.upsert()`
  - Changed collection to `"carestaffs"`
  - Renamed variable from `password` to `hashed_password` for clarity
- **get_nurse_by_id()**: New method to retrieve and cast Nurse instances with role validation

### cli/doctor_cli.py
- **register()**: 
  - Removed redundant `new_doctor.register()` call
  - Set `self.current_doctor = new_doctor` after successful registration
  - Improved success message
- **login()**: 
  - Changed from `Doctor.get_carestaff_by_id()` to `Doctor.get_doctor_by_id()`
  - Fixed prompt formatting (added ": " to registration prompt)

### cli/nurse_cli.py
- **register()**: 
  - Fixed success message text ("Doctor ID" → "Nurse ID")
  - Set `self.current_nurse = new_nurse` after successful registration
- **login()**: 
  - Changed from `Nurse.get_carestaff_by_id()` to `Nurse.get_nurse_by_id()`
  - Removed duplicate retrieval call after password input
  - Fixed prompt formatting (added ": " to registration prompt)

## Test Results

All 52 tests passing:
- ✅ 46 carestaff tests (including previously failing `test_add_appointment`)
- ✅ 6 serialization tests

## Verification

Manual testing confirms:
1. ✅ Doctor registration works and persists to DataStore
2. ✅ Doctor retrieval by ID works with proper type casting
3. ✅ Doctor login with correct password succeeds
4. ✅ Doctor login with wrong password fails appropriately
5. ✅ Nurse registration works and persists to DataStore
6. ✅ Nurse retrieval by ID works with proper type casting
7. ✅ Nurse login with correct password succeeds
8. ✅ Password hashing with bcrypt functions correctly throughout the flow

## Security Note

Passwords are properly hashed using bcrypt before storage:
- Registration: `bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')`
- Login: `bcrypt.checkpw(credentials.get("password").encode('utf-8'), self.password.encode('utf-8'))`

The hashed password is stored in the DataStore and never the plain text password.
