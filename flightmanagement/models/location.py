import re
from dataclasses import dataclass
from flightmanagement.error import FieldValidationError, DomainValidationError

@dataclass(frozen = True)
class Location:
    location_type: str
    location_name: str
    country: str
        
    location_id: int | None = None
    icao_location_code: str | None = None
    iata_airport_code: str | None = None
    town_or_city: str | None = None
    state_or_county: str | None = None
    geographic_region: str | None = None
    decimal_latitude: float | None = None
    decimal_longitude: float | None = None

    def __post_init__(self):        
        self._validate_fields()
        self._validate_domain()
        
    def __str__(self):
        return f"{self.iata_airport_code if self.iata_airport_code else self.icao_location_code} ({self.location_name})"

    def _validate_fields(self) -> None:
        if not self.location_type:
            raise FieldValidationError("location_type", "Location type is missing.")

        if not self.location_name:
            raise FieldValidationError("location_name", "Location name is missing.")

        if self.location_type == "Airport":
            if not self.iata_airport_code:
                raise FieldValidationError("iata_airport_code", "Airport code is missing.")
            elif not re.fullmatch(r"[A-Z]{3}", self.iata_airport_code):
                raise FieldValidationError("iata_airport_code", "Airport code should be 3 uppercase letters (e.g. LHR).")
        else:
            if self.iata_airport_code:
                raise FieldValidationError("iata_airport_code", "Non-airport locations cannot have an airport code.")

        if self.location_type != "Airport":
            if not self.icao_location_code:
                raise FieldValidationError("icao_location_code", "ICAO location code is required for non-airport locations.")
        
        if self.icao_location_code and not re.fullmatch(r"[A-Z]{4}", self.icao_location_code):
            raise FieldValidationError("iata_airport_code", "ICAO location code should be 4 uppercase letters (e.g. EGLL).")

        if self.location_type == "Airport" and not self.town_or_city:
            raise FieldValidationError("town_or_city", "Town or city is missing.")

        if self.town_or_city and not self._is_valid_name(self.town_or_city):
            raise FieldValidationError("town_or_city", "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if self.state_or_county and not self._is_valid_name(self.state_or_county):
            raise FieldValidationError("state_or_county", "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if not self.country:
            raise FieldValidationError("country", "Country is missing.")

        if self.country and not self._is_valid_name(self.country):
            raise FieldValidationError("country", "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if self.geographic_region and not self._is_valid_name(self.geographic_region):
            raise FieldValidationError("geographic_region", "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if self.decimal_latitude:
            if not self._is_float(self.decimal_latitude):
                raise FieldValidationError("decimal_latitude", "Latitude must be a number.")
            if not (-90 <= self.decimal_latitude <= 90):
                raise FieldValidationError("decimal_latitude", "Latitude must be between -90 and 90 degrees.")

        if self.decimal_longitude:
            if not self._is_float(self.decimal_longitude):
                raise FieldValidationError("decimal_longitude", "Longitude must be a number.")
            if not (-180 <= self.decimal_longitude <= 180):
                raise FieldValidationError("decimal_longitude", "Longitude must be between -180 and 180 degrees.")
        

    def _validate_domain(self) -> None:
        if (self.decimal_latitude and not self.decimal_longitude) or (self.decimal_longitude and not self.decimal_latitude):
            raise DomainValidationError("If coordinates are entered, a latitude and longitude are both required.")

    def _is_float(self, value: float) -> bool:
        try:
            float(value)
        except:
            return False
        
        return True

    def _is_valid_name(self, string: str) -> bool:        
        # Return true if all characters are letters, spaces, hyphens or apostrophes
        return all(char.isalpha() or char in {" ", "-", "'"} for char in string)
    
    def to_dict(self) -> dict:
        data = {
            "location_type": self.location_type, 
            "icao_location_code": self.icao_location_code,
            "iata_airport_code": self.iata_airport_code, 
            "location_name": self.location_name,
            "town_or_city": self.town_or_city,
            "state_or_county": self.state_or_county,
            "country": self.country,
            "geographic_region": self.geographic_region,
            "decimal_latitude": self.decimal_latitude,
            "decimal_longitude": self.decimal_longitude
        }
        return data

@dataclass(frozen = True)
class Terminal:
    location_id: int
    terminal_name: str
        
    terminal_id: int | None = None

    def __post_init__(self):
        self._validate_fields()
        self._validate_domain()
        
    def __str__(self):
        return f"{self.terminal_name}"

    def _validate_fields(self) -> None:
        if not self.terminal_name:
            raise FieldValidationError("terminal_name", "Terminal name is missing.")

    def _validate_domain(self) -> None:
        pass

    def to_dict(self) -> dict:
        data = {
            "location_id": self.location_id,
            "terminal_name": self.terminal_name
        }
        return data

@dataclass(frozen = True)
class Gate:
    terminal_id: int
    gate_number: str
        
    gate_id: int | None = None

    def __post_init__(self):
        self._validate_fields()
        self._validate_domain()

    def __str__(self):
        return f"{self.gate_number}"
    
    def _validate_fields(self) -> None:
        if not self.gate_number:
            raise FieldValidationError("gate_number", "Gate number is missing.")

    def _validate_domain(self) -> None:
        pass

    def to_dict(self) -> dict:
        data = {
            "terminal_id": self.terminal_id,
            "gate_number": self.gate_number
        }
        return data
