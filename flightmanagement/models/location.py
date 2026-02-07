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
        
        self._validate()
        self._correct_case()
        
    def __str__(self):
        return f"{self.iata_airport_code} ({self.location_name})"

    def _validate(self):

        # Field-level validations
        if not self.location_type:
            raise FieldValidationError(field = "location_type", message = "Location type is missing.")

        if not self.location_name:
            raise FieldValidationError(field = "location_name", message = "Location name is missing.")

        if self.location_type == "Airport":
            if not self.iata_airport_code:
                raise FieldValidationError(field = "iata_airport_code", message = "Airport code is missing.")
            elif not re.fullmatch(r"[A-Z]{3}", self.iata_airport_code):
                raise FieldValidationError(field = "iata_airport_code", message = "Airport code should be 3 uppercase letters (e.g. LHR).")
        else:
            if self.iata_airport_code:
                raise FieldValidationError(field = "iata_airport_code", message = "Non-airport locations cannot have an airport code.")

        if self.location_type != "Airport":
            if not self.icao_location_code:
                raise FieldValidationError(field = "icao_location_code", message = "ICAO location code is required for non-airport locations.")
        
        if self.icao_location_code and not re.fullmatch(r"[A-Z]{4}", self.icao_location_code):
            raise FieldValidationError(field = "iata_airport_code", message = "ICAO location code should be 4 uppercase letters (e.g. EGLL).")

        if self.location_type == "Airport" and not self.town_or_city:
            raise FieldValidationError(field = "town_or_city", message = "Town or city is missing.")

        if self.town_or_city and not self._is_valid_name(self.town_or_city):
            raise FieldValidationError(field = "town_or_city", message = "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if self.state_or_county and not self._is_valid_name(self.state_or_county):
            raise FieldValidationError(field = "state_or_county", message = "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if not self.country:
            raise FieldValidationError(field = "country", message = "Country is missing.")

        if self.country and not self._is_valid_name(self.country):
            raise FieldValidationError(field = "country", message = "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if self.geographic_region and not self._is_valid_name(self.geographic_region):
            raise FieldValidationError(field = "geographic_region", message = "Name may only contain upper and lower case letters (including diacritics), apostrophes and hyphens.")
        
        if self.decimal_latitude:
            if not self._is_float(self.decimal_latitude):
                raise FieldValidationError(field = "decimal_latitude", message = "Latitude must be a number.")
            if not (-90 <= self.decimal_latitude <= 90):
                raise FieldValidationError(field = "decimal_latitude", message = "Latitude must be between -90 and 90 degrees.")

        if self.decimal_longitude:
            if not self._is_float(self.decimal_longitude):
                raise FieldValidationError(field = "decimal_longitude", message = "Longitude must be a number.")
            if not (-180 <= self.decimal_longitude <= 180):
                raise FieldValidationError(field = "decimal_longitude", message = "Longitude must be between -180 and 180 degrees.")
        
        # Domain-level validations
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
    
    def _correct_case(self):
        # Ensure correct capitalisation
        if self.icao_location_code is not None:
            object.__setattr__(self, "icao_location_code", self.icao_location_code.upper())
        if self.iata_airport_code is not None:
            object.__setattr__(self, "iata_airport_code", self.iata_airport_code.upper())
        if self.town_or_city is not None:
            object.__setattr__(self, "town_or_city", self.town_or_city.title())
        if self.state_or_county is not None:
            object.__setattr__(self, "state_or_county", self.state_or_county.title())
        if self.country is not None:
            object.__setattr__(self, "country", self.country.title())
        if self.geographic_region is not None:
            object.__setattr__(self, "geographic_region", self.geographic_region.title())

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
        pass
        #self._validate()
        #self._correct_case()
        
    def __str__(self):
        return f"{self.terminal_name}"

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
        pass
        #self._validate()
        #self._correct_case()
        
    def __str__(self):
        return f"{self.gate_number}"
    
    def to_dict(self) -> dict:
        data = {
            "terminal_id": self.terminal_id,
            "gate_number": self.gate_number
        }
        return data
