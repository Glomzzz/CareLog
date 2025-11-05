"""Admin domain helpers that use the model classes and DataStore.

This module replaces the previous implementation which directly read and
wrote `data/carelog.json`. It now uses the higher-level model objects in
`app.model.patient` and `app.model.carestaff` and the `DataStore` helpers in
`app.data.datastore`.

The public methods keep the original names and behavior where reasonable
but delegate storage/serialization to the models.
"""

from typing import Iterable, List, Any

from app.model.user import User
from app.model.patient import Patient
from app.model.carestaff import CareStaff
from app.data.datastore import DataStore

import bcrypt
salt = bcrypt.gensalt()

class Admin(User):
    """Admin helper to manage patients and care staff via model classes.

    Note: methods accept either model instances or plain dicts for
    backwards-compatibility with existing CLI/tests. When given dicts, this
    class will attempt to construct the appropriate model object before
    persisting.
    """
    
    @classmethod
    def all_admin_ids(cls) -> List[str]:
        """Return a list of all admin IDs in the system."""
        admins = DataStore.get_collection("admins")
        return [admin.get("id") for admin in admins if "id" in admin]

    def __init__(self, name: str = "admin", id: str = "admin", phone: str = "", email: str = "", password: str = ""): 
        super().__init__(
            user_id=id,
            name=name,
            email=email or f"{id}@carelog.local",
            password=password or "",
            role="admin",
        )
        self.phone = phone

    # ----------------------- Patients ---------------------------------
    def add_new_patients(self, patients: Iterable[Any]) -> None:
        """Add one or more patients.

        Each item may be a Patient instance or a dict with keys
        (id, name, email, phone, password).
        """
        added = []
        for item in patients:
            if isinstance(item, Patient):
                DataStore.append_to_collection("patients", item.to_dict())
                added.append(item.to_dict())
            elif isinstance(item, dict):
                # Construct Patient from plain dict (expects plain PHI and a password)
                p = Patient(
                    id=item.get("id"),
                    name=item.get("name"),
                    email=item.get("email"),
                    phone=item.get("phone"),
                    password=item.get("password") or item.get("password_hash"),
                )
                DataStore.append_to_collection("patients", p.to_dict())
                added.append(p.to_dict())
            else:
                # unknown object: ignore for robustness
                continue

        print("Patient(s) added successfully!")
        for patient in added:
            for k, v in patient.items():
                print(f"{k}: {v}")

    def update_patients_information(self, id: str, choice: int, information: str) -> bool:
        """Update patient's name/email/phone.

        choice: 1=name, 2=email, 3=phone
        Returns True on success, False if patient not found.
        """
        stored = DataStore.get_by_id("patients", "id", id)
        if not stored:
            print("Patient not found. Please try again.")
            return False

        # Reconstruct Patient to get plaintext values
        try:
            existing = Patient.patient_from_dict(stored)
            plain_name = existing.get_decrypted_name()
            plain_email = existing.get_decrypted_email()
            plain_phone = existing.get_decrypted_phone()
        except Exception:
            # If reconstruction fails, fall back to raw dict values
            plain_name = stored.get("name")
            plain_email = stored.get("email")
            plain_phone = stored.get("phone")

        if choice == 1:
            plain_name = information
        elif choice == 2:
            plain_email = information
        elif choice == 3:
            plain_phone = information
        else:
            print("Invalid choice")
            return False

        # Create a new Patient object using the existing key to preserve encryption
        new_patient = Patient(
            id=stored.get("id"),
            name=plain_name,
            email=plain_email,
            phone=plain_phone,
            password_hash=stored.get("password_hash"),
            key=bytes.fromhex(stored.get("key")) if stored.get("key") else None,
        )
        DataStore.upsert("patients", "id", new_patient.to_dict())

        print(f"Patient information for patient ID {new_patient.id} successfully changed!")
        for k, v in new_patient.to_dict().items():
            print(f"{k}: {v}")
        return True

    def remove_patients(self, id_list: Iterable[str]) -> None:
        """Remove patients by id list."""
        removed = []
        for pid in id_list:
            stored = DataStore.get_by_id("patients", "id", pid)
            if stored:
                removed.append(stored)
                DataStore.delete_by_id("patients", "id", pid)

        print("Patient(s) removed successfully!")
        for p in removed:
            for k, v in p.items():
                print(f"{k}: {v}")

    # ----------------------- CareStaffs ---------------------------------
    def add_new_carestaffs(self, carestaffs: Iterable[Any]) -> None:
        """Add new care staff entries.

        Accepts CareStaff instances or dicts with fields accepted by CareStaff.from_dict.
        """
        added = []
        for item in carestaffs:
            if isinstance(item, CareStaff):
                item.save()
                added.append(item.to_dict())
            elif isinstance(item, dict):
                cs = CareStaff.from_dict(item)
                cs.save()
                added.append(cs.to_dict())

        print("Carestaff(s) added successfully!")
        for cs in added:
            for k, v in cs.items():
                print(f"{k}: {v}")

    def update_carestaffs_information(self, id: str, department: str, specialization: str) -> bool:
        """Update carestaff department and specialization."""
        cs = CareStaff.get_carestaff_by_id(id)
        if not cs:
            print("Carestaff not found.")
            return False
        cs.department = department
        cs.specialization = specialization
        cs.save()

        print(f"Carestaff information for carestaff ID {id} successfully changed!")
        for k, v in cs.to_dict().items():
            print(f"{k}: {v}")
        return True

    def remove_carestaffs(self, id_list: Iterable[str]) -> None:
        """Remove carestaff(s) by id list."""
        removed = []
        for cid in id_list:
            stored = DataStore.get_by_id("carestaffs", "id", cid)
            if stored:
                removed.append(stored)
                DataStore.delete_by_id("carestaffs", "id", cid)

        print("Carestaff(s) removed successfully!")
        for cs in removed:
            for k, v in cs.items():
                print(f"{k}: {v}")

    # ----------------------- Search / Queries ---------------------------
    def search_patient_information(self, id: str) -> None:
        """Print patient info (decrypted) for given id."""
        stored = DataStore.get_by_id("patients", "id", id)
        if not stored:
            print("Patient not found! Please try again.")
            return
        try:
            p = Patient.patient_from_dict(stored)
            print("Patient found! The following are the patient's information found:")
            print(f"id: {p.id}")
            print(f"name: {p.get_decrypted_name()}")
            print(f"email: {p.get_decrypted_email()}")
            print(f"phone: {p.get_decrypted_phone()}")
        except Exception:
            # Fallback to raw dict print
            print("Patient found! The following are the patient's information found:")
            for k, v in stored.items():
                print(f"{k}: {v}")

    def number_of_patients(self, id: str) -> int | None:
        """Return number of patients assigned to a carestaff."""
        stored = DataStore.get_by_id("carestaffs", "id", id)
        if not stored:
            return None
        # support both legacy 'assignedPatients' and new 'assigned_patients'
        assigned = stored.get("assigned_patients") or stored.get("assignedPatients") or []
        return len(assigned)

    def search_carestaffs_by_keyword(self, keyword: str) -> None:
        """Search carestaffs by name/department/specialization."""
        all_cs = DataStore.get_collection("carestaffs")
        found = []
        for cs in all_cs:
            name = (cs.get("name") or "").lower()
            dept = (cs.get("department") or "").lower()
            spec = (cs.get("specialization") or "").lower()
            if keyword.lower() in name or keyword.lower() in dept or keyword.lower() in spec:
                found.append(cs)

        if found:
            print(f"{len(found)} carestaff(s) found matching the keyword '{keyword}':")
            for cs in found:
                print("-----")
                for k, v in cs.items():
                    print(f"{k}: {v}")
        else:
            print(f"No carestaff found matching the keyword '{keyword}'.")

    def search_patients_by_keyword(self, keyword: str) -> None:
        """Search patients by decrypted name/email/phone."""
        all_pat = DataStore.get_collection("patients")
        found = []
        for p in all_pat:
            try:
                obj = Patient.patient_from_dict(p)
                name = obj.get_decrypted_name().lower()
                email = obj.get_decrypted_email().lower()
                phone = obj.get_decrypted_phone().lower()
            except Exception:
                # fall back to raw stored values
                name = (p.get("name") or "").lower()
                email = (p.get("email") or "").lower()
                phone = (p.get("phone") or "").lower()

            if keyword.lower() in name or keyword.lower() in email or keyword.lower() in phone:
                found.append(p)

        if found:
            print(f"{len(found)} patient(s) found matching the keyword '{keyword}':")
            for pat in found:
                print("-----")
                for k, v in pat.items():
                    print(f"{k}: {v}")
        else:
            print(f"No patient found matching the keyword '{keyword}'.")
    @classmethod
    def get_admin_by_id(cls, admin_id: str):
        """Get an admin by ID from the datastore and return an Admin instance.

        The datastore stores admin records as plain dicts; this helper reconstructs
        an Admin object to provide the higher-level methods (login, update, etc.).
        """
        data = DataStore.get_by_id("admins", "id", admin_id)
        if not data:
            return None
        # Reconstruct Admin using stored values; fall back to sensible defaults.
        return cls(
            name=data.get("name", "admin"),
            id=data.get("id", admin_id),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
        )

    @classmethod
    def register(cls, name: str, id: str, email: str, password: str, phone: str = ""):
        """Register a new admin in the system.

        Accepts an optional phone value and persists a plain dict keyed by
        `id` so the record can be retrieved by older code that expects that shape.
        Returns an Admin instance.
        """
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        admin = cls(
            name,
            id,
            phone=phone,
            email=email,
            password=hashed_password,
        )
        # Persist a plain dict with an `id` key so DataStore.get_by_id works as expected.
        DataStore.upsert("admins", "id", admin.to_dict())
        return admin