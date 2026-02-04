from datetime import datetime, date, time
from dataclasses import dataclass
import re

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
        if not self.__is_valid_flight_number():
            raise ValueError("Invalid flight number")
        
        if not self.aircraft_id:
            raise ValueError("Invalid aircraft ID")
        
        if not self.origin_location_id:
            raise ValueError("Invalid origin ID")
        
        if not self.destination_location_id or self.destination_location_id == self.origin_location_id:
            raise ValueError("Invalid destination ID")
        
        if not self.__is_valid_status():
            raise ValueError("Invalid status")

        if not self.__is_valid_scheduled_arrival_time():
            raise ValueError(f"Scheduled arrival time is not later than scheduled departure time")

        if not self.__is_valid_actual_arrival_time():
            raise ValueError("Actual arrival time is not later than actual departure time")

        if self.captain_id and self.first_officer_id == self.captain_id:
            raise ValueError("Invalid first officer ID")

    def __str__(self):        
        departure = datetime.strftime(datetime.combine(self.scheduled_departure_date, self.scheduled_arrival_time), "%Y-%m-%d %H:%M")
        return f"{self.flight_number} (departure: {departure}, status: {self.flight_status})"

    def __is_valid_flight_number(self) -> bool:
        if self.flight_number and re.fullmatch(r"ZMY[0-9]+", self.flight_number):
            return True
        return False

    def __is_valid_status(self) -> bool:
        if self.flight_status in ["Scheduled", "On time", "Delayed", "Boarding", "Closed", "Departed", "Arrived"]:
            return True
        return False

    def __is_valid_scheduled_arrival_time(self):     
        if datetime.combine(self.scheduled_arrival_date, self.scheduled_arrival_time) > datetime.combine(self.scheduled_departure_date, self.scheduled_departure_time):
            return True
        return False
    
    def __is_valid_actual_arrival_time(self):
        if self.confirmed_arrival_date is None or self.confirmed_arrival_time is None or self.confirmed_departure_date is None or self.confirmed_departure_time is None:
            return True
        if datetime.combine(self.confirmed_arrival_date, self.confirmed_arrival_time) > datetime.combine(self.confirmed_departure_date, self.confirmed_departure_time):
            return True
        return False

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