from dataclasses import dataclass
from datetime import datetime, date
import re
from flightmanagement.error import FieldValidationError, DomainValidationError

@dataclass(frozen = True)
class Pilot:
    employee_number: str
    first_name: str
    family_name: str    
    employment_start_date: date
    employment_status: str = "Current"

    staff_member_id: int | None = None
    employment_end_date: date | None = None
    license_number: str | None = None
    license_type: str | None = None
    license_expiration_date: date | None = None

    def __post_init__(self):
        self._validate_fields()
        self._validate_domain()

        if not self._is_valid_name(self.first_name):
            raise ValueError("Invalid first name")
        
        if not self._is_valid_name(self.family_name):
            raise ValueError("Invalid family name")

    def __str__(self):
        return f"{self.first_name} {self.family_name}"

    def _validate_fields(self) -> None:
        if not self.first_name:
            raise FieldValidationError("first_name", "First name is missing.")

        if not self._is_valid_name(self.first_name):
            raise FieldValidationError("first_name", "Name may only contain letters (including diacritics), hyphens and apostrophes.")
        
        if not self.family_name:
            raise FieldValidationError("family_name", "Family name is missing.")
        
        if not self._is_valid_name(self.family_name):
            raise FieldValidationError("family_name", "Name may only contain letters (including diacritics), hyphens and apostrophes.")
    
        if not self.employment_start_date:
            raise FieldValidationError("employment_start_date", "Employment start date is missing.")
        
        if not self.employment_status:
            raise FieldValidationError("employment_status", "Employment status is missing.")

    def _validate_domain(self) -> None:
        if self.employment_status == "Current" and self.employment_end_date is not None:
            raise DomainValidationError("Current employees cannot have an employment end date.")
        
        if self.employment_status == "Left" and self.employment_end_date is None:
            raise DomainValidationError("Employees who have left must have an employment end date.")

    def _is_valid_name(self, string: str) -> bool:        
        # Return true if all characters are letters, spaces, hyphens or apostrophes
        return all(char.isalpha() or char in {" ", "-", "'"} for char in string)

    def to_dict_staff_member(self) -> dict:
        data = {
            "employee_number": self.employee_number,
            "first_name": self.first_name, 
            "family_name": self.family_name,
            "employment_status": self.employment_status,
            "employment_start_date": self.employment_start_date.strftime("%Y-%m-%d"),
            "employment_end_date": self.employment_end_date.strftime("%Y-%m-%d") if self.employment_end_date else None
        }
        return data

    def to_dict_pilot(self, staff_member_id: int | None = None) -> dict:
        data = {
            "staff_member_id": staff_member_id,
            "license_number": self.license_number,
            "license_type": self.license_type,
            "license_expiration_date": self.license_expiration_date.strftime("%Y-%m-%d") if self.license_expiration_date else None
        }
        return data