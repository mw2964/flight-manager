from datetime import datetime, date, time
from dataclasses import dataclass
import re
from flightmanagement.error import FieldValidationError, DomainValidationError

@dataclass(frozen = True)
class Flight:    
    flight_number: str    
    origin_location_id: int
    destination_location_id: int
    scheduled_departure_date: date
    scheduled_departure_time: time
    scheduled_arrival_date: date
    scheduled_arrival_time: time
    flight_status: str

    flight_id: int | None = None
    aircraft_id: int | None = None
    departure_gate_id: int | None = None
    arrival_gate_id: int | None = None
    captain_id: int | None = None
    first_officer_id: int | None = None
    confirmed_departure_date: date | None = None
    confirmed_departure_time: time | None = None
    confirmed_arrival_date: date | None = None
    confirmed_arrival_time: time | None = None
    
    def __post_init__(self):
        self._validate_fields()
        self._validate_domain()

    def __str__(self):        
        departure = datetime.strftime(datetime.combine(self.scheduled_departure_date, self.scheduled_departure_time), "%Y-%m-%d %H:%M")
        return f"{self.flight_number} (departure: {departure}, status: {self.flight_status})"

    def _validate_fields(self) -> None:
        if not self.flight_number:
            raise FieldValidationError("flight_number", "Flight number is missing.")

        if self.flight_number and not re.fullmatch(r"ZMY[0-9]+", self.flight_number):
            raise FieldValidationError("flight_number", "Flight number must be 'ZMY' followed by a number.")
        
        if not self.origin_location_id:
            raise FieldValidationError("origin_location_id", "Origin location is missing.")
        
        if not self.destination_location_id:
            raise FieldValidationError("destination_location_id", "Desination location is missing.")
        
        if self.destination_location_id == self.origin_location_id:
            raise FieldValidationError("destination_location_id", "Destination must be different to the origin.")
        
        if self.flight_status not in ["Scheduled", "On time", "Delayed", "Boarding", "Closed", "Departed", "Arrived"]:
            raise ValueError("Invalid status.")
        
        if self.captain_id and self.first_officer_id == self.captain_id:
            raise FieldValidationError("first_officer_id", "First officer must be different to the selected captain.")

    def _validate_domain(self) -> None:
        if datetime.combine(self.scheduled_arrival_date, self.scheduled_arrival_time) <= datetime.combine(self.scheduled_departure_date, self.scheduled_departure_time):
            raise DomainValidationError(f"Scheduled arrival time must be after the scheduled departure time.")

        if self.confirmed_arrival_date is not None and self.confirmed_arrival_time is not None and self.confirmed_departure_date is not None and self.confirmed_departure_time is not None:
            if datetime.combine(self.confirmed_arrival_date, self.confirmed_arrival_time) <= datetime.combine(self.confirmed_departure_date, self.confirmed_departure_time):
                raise DomainValidationError("Confirmed arrival time must be after the confirmed departure time.")

    def to_dict(self) -> dict:
        data = {
            "aircraft_id": self.aircraft_id,
            "origin_location_id": self.origin_location_id, 
            "destination_location_id": self.destination_location_id,
            "departure_gate_id": self.departure_gate_id,
            "arrival_gate_id": self.arrival_gate_id,
            "captain_id": self.captain_id,
            "first_officer_id": self.first_officer_id,
            "flight_number": self.flight_number,
            "scheduled_departure_date": self.scheduled_departure_date.strftime("%Y-%m-%d"),
            "scheduled_departure_time": self.scheduled_departure_time.strftime("%H:%M"),
            "scheduled_arrival_date": self.scheduled_arrival_date.strftime("%Y-%m-%d"),
            "scheduled_arrival_time": self.scheduled_arrival_time.strftime("%H:%M"),
            "confirmed_departure_date": self.confirmed_departure_date.strftime("%Y-%m-%d") if self.confirmed_departure_date else None,
            "confirmed_departure_time": self.confirmed_departure_time.strftime("%H:%M") if self.confirmed_departure_time else None,
            "confirmed_arrival_date": self.confirmed_arrival_date.strftime("%Y-%m-%d") if self.confirmed_arrival_date else None,
            "confirmed_arrival_time": self.confirmed_arrival_time.strftime("%H:%M") if self.confirmed_arrival_time else None,
            "flight_status": self.flight_status
        }
        return data