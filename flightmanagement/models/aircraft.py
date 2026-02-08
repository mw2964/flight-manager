import re
from dataclasses import dataclass
from flightmanagement.error import FieldValidationError, DomainValidationError

@dataclass(frozen = True)
class Aircraft:
    aircraft_type_id: int
    registration: str
    aircraft_status: str = "Active"

    aircraft_id: int | None = None
    manufacturer_serial_no: int | None = None
    icao_hex: str | None = None
    
    def __post_init__(self):
        self._validate_fields()
        self._validate_domain()

    def __str__(self):
        return f"{self.registration}"

    def _validate_fields(self):
        if not self.aircraft_type_id:
            raise FieldValidationError(field = "aircraft_type_id", message = "Aircraft type is missing.")
        
        if not self.registration:
            raise FieldValidationError(field = "registration", message = "Registration is missing.")
        
        if self.registration and not re.fullmatch(r"[A-Z]{1,2}-[A-Z]{3,4}", self.registration):
            raise FieldValidationError(field = "registration", message = "Registration must be one or two letters plus a hypen followed by three or four letters.")

        if not self.aircraft_status or self.aircraft_status not in ["Active", "Inactive", "Decommissioned"]:
            raise FieldValidationError(field = "aircraft_status", message = "Aircraft status is missing or invalid.")

    def _validate_domain(self):
        pass

    def to_dict(self) -> dict:
        data = {
            "aircraft_type_id": self.aircraft_type_id,
            "registration": self.registration, 
            "manufacturer_serial_no": self.manufacturer_serial_no,
            "icao_hex": self.icao_hex,
            "aircraft_status": self.aircraft_status
        }
        return data

@dataclass(frozen = True)
class AircraftType:
    manufacturer: str
    model: str

    aircraft_type_id: int | None = None
    icao_type: str | None = None

    def __post_init__(self):
        self._validate_fields()
        self._validate_domain()

    def __str__(self):
        return f"{self.manufacturer} {self.model}"
    
    def _validate_fields(self):
        if not self.manufacturer:
            raise FieldValidationError(field = "manufacturer", message = "Manufacturer is missing.")
        
        if not self.model:
            raise FieldValidationError(field = "model", message = "Model is missing.")

    def _validate_domain(self):
        pass

    def to_dict(self) -> dict:
        data = {
            "manufacturer": self.manufacturer,
            "model": self.model, 
            "icao_type": self.icao_type
        }
        return data