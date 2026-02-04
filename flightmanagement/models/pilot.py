from dataclasses import dataclass
from datetime import datetime, date
import re

@dataclass(frozen = True)
class Pilot:
    employee_number: str
    first_name: str
    family_name: str    
    employment_start_date: date
    employment_status: str = "Current"

    staff_id: int | None = None
    employment_end_date: date | None = None
    license_number: str | None = None
    license_type: str | None = None
    license_expiration_date: date | None = None

    def __post_init__(self):
        if not self.__is_valid_name(self.first_name):
            raise ValueError("Invalid first name")
        
        if not self.__is_valid_name(self.family_name):
            raise ValueError("Invalid family name")

    def __str__(self):
        return f"{self.first_name} {self.family_name}"

    def __is_valid_name(self, name: str | None) -> bool:
        if name and re.fullmatch(r"[A-Za-z\s-]+", name):
            return True
        return False

    def to_dict_staff(self) -> dict:
        data = {
            "employee_number": self.employee_number,
            "first_name": self.first_name, 
            "family_name": self.family_name,
            "employment_status": self.employment_status,
            "employment_start_date": self.employment_start_date.strftime("%Y-%m-%d"),
            "employment_end_date": self.employment_end_date.strftime("%Y-%m-%d") if self.employment_end_date else None
        }
        return data

    def to_dict_pilot(self, staff_id: int | None = None) -> dict:
        data = {
            "staff_id": staff_id,
            "license_number": self.license_number,
            "license_type": self.license_type,
            "license_expiration_date": self.license_expiration_date.strftime("%Y-%m-%d") if self.license_expiration_date else None
        }
        return data