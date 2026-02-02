from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Location:
    location_type: str
    location_name: str
        
    location_id: int | None = None
    icao_location_code: str | None = None
    iata_airport_code: str | None = None
    town_or_city: str | None = None
    state_or_county: str | None = None
    country: str | None = None
    geographic_region: str | None = None
    decimal_latitude: float | None = None
    decimal_longitude: float | None = None

    def __post_init__(self):
        
        self.__validate_attributes()
        self.__correct_case()
        
    def __str__(self):
        return f"{self.iata_airport_code} ({self.location_name})"

    def __validate_attributes(self):        
        if not self.__is_valid_iata_airport_code():
            raise ValueError("Invalid airport code")
        if not self.__is_valid_icao_location_code():
            raise ValueError("Invalid ICAO location code")
        if not self.__is_valid_alpha(self.town_or_city):
            raise ValueError("Invalid town/city name")
        if not self.__is_valid_alpha(self.state_or_county):
            raise ValueError("Invalid state/county/province name")
        if not self.__is_valid_alpha(self.country):
            raise ValueError("Invalid country name")
        if not self.__is_valid_alpha(self.geographic_region):
            raise ValueError("Invalid geograpic region name")
        if not self.__is_valid_latitude():
            raise ValueError("Invalid latitude")
        if not self.__is_valid_longitude():
            raise ValueError("Invalid longitude")

    def __is_valid_iata_airport_code(self) -> bool:

        # If the location is an airport, it must have a valid airport code
        if self.location_type == "Airport" and self.iata_airport_code is not None and re.fullmatch(r"[A-Z]{3}", self.iata_airport_code):
            return True
        
        # If the location is not an airport, it must not have an airport code
        if self.location_type != "Airport" and self.iata_airport_code is None:
            return True

        return False

    @staticmethod
    def is_valid_iata_airport_code(iata_airport_code: str, location_type: str) -> bool:

        # If the location is an airport, it must have a valid airport code
        if location_type == "Airport" and iata_airport_code is not None and re.fullmatch(r"[A-Z]{3}", iata_airport_code):
            return True
        
        # If the location is not an airport, it must not have an airport code
        if location_type != "Airport" and iata_airport_code is None:
            return True

        return False

    def __is_valid_icao_location_code(self) -> bool:

        # If the location is not an airport, it must have a location code
        if self.location_type != "Airport" and self.icao_location_code is None:
            return False
        
        # If the location has a code, it must be of the correct format
        if self.icao_location_code is not None and not re.fullmatch(r"[A-Z]{4}", self.icao_location_code):
            return False
        
        return True

    def __is_valid_latitude(self):

        # Field is not mandatory
        if self.decimal_latitude is None:
            return True
        
        # Validate data type
        try:
            float(self.decimal_latitude)
        except:
            return False
        
        # Validate range
        if -90 <= self.decimal_latitude <= 90:
            return True
        
        return False
    
    def __is_valid_longitude(self):

        # Field is not mandatory
        if self.decimal_longitude is None:
            return True
        
        # Validate data type
        try:
            float(self.decimal_longitude)
        except:
            return False
        
        # Validate range
        if -180 <= self.decimal_longitude <= 180:
            return True
        
        return False

    def __is_valid_alpha(self, string: str | None, optional: bool = True):
        
        # Missing is ok if the attribute isn't mandatory
        if string is None:
            return optional
        
        # Return true if all characters are letters, spaces, hyphens or apostrophes
        return all(char.isalpha() or char in {" ", "-", "'"} for char in string)
    
    def __correct_case(self):
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

@dataclass(frozen=True)
class Terminal:
    location_id: int
    terminal_name: str
        
    terminal_id: int | None = None

    def __post_init__(self):
        pass
        #self.__validate_attributes()
        #self.__correct_case()
        
    def __str__(self):
        return f"{self.terminal_name}"

    def to_dict(self) -> dict:
        data = {
            "location_id": self.location_id,
            "terminal_name": self.terminal_name
        }
        return data


@dataclass(frozen=True)
class Gate:
    terminal_id: int
    gate_number: str
        
    gate_id: int | None = None

    def __post_init__(self):
        pass
        #self.__validate_attributes()
        #self.__correct_case()
        
    def __str__(self):
        return f"{self.gate_number}"
    
    def to_dict(self) -> dict:
        data = {
            "terminal_id": self.terminal_id,
            "gate_number": self.gate_number
        }
        return data
