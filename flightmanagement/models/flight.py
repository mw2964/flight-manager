from datetime import datetime
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Flight:    
    flight_number: str
    aircraft_id: int
    origin_id: int
    destination_id: int
    departure_time_scheduled: datetime
    arrival_time_scheduled: datetime
    status: str = "Scheduled"

    id: int | None = None
    pilot_id: int | None = None
    copilot_id: int | None = None
    departure_time_actual: datetime | None = None
    arrival_time_actual: datetime | None = None
    
    def __post_init__(self):
        if not self.__is_valid_flight_number():
            raise ValueError("Invalid flight number")
        
        if not self.aircraft_id:
            raise ValueError("Invalid aircraft ID")
        
        if not self.origin_id:
            raise ValueError("Invalid origin ID")
        
        if not self.destination_id or self.destination_id == self.origin_id:
            raise ValueError("Invalid destination ID")
        
        if not self.__is_valid_status():
            raise ValueError("Invalid status")

        if not self.__is_valid_scheduled_arrival_time():
            raise ValueError(f"Scheduled arrival time is not later than scheduled departure time")

        if not self.__is_valid_actual_arrival_time():
            raise ValueError("Actual arrival time is not later than actual departure time")

        if self.pilot_id and self.copilot_id == self.pilot_id:
            raise ValueError("Invalid copilot ID")

    def __is_valid_flight_number(self) -> bool:
        if self.flight_number and re.fullmatch(r"ZMY[0-9]+", self.flight_number):
            return True
        return False

    def __is_valid_status(self) -> bool:
        if self.status in ["Scheduled", "On time", "Delayed", "Boarding", "Closed", "Departed", "Arrived"]:
            return True
        return False

    def __is_valid_scheduled_arrival_time(self):
        if not self.arrival_time_scheduled:
            return True        
        if self.arrival_time_scheduled > self.departure_time_scheduled:
            return True
        return False
    
    def __is_valid_actual_arrival_time(self):
        if not self.arrival_time_actual or not self.departure_time_actual:
            return True
        if self.arrival_time_actual > self.departure_time_actual:
            return True
        return False

    def __str__(self):
        if self.departure_time_scheduled is None:
            departure = ""
        else:
            departure = datetime.strftime(self.departure_time_scheduled, "%Y-%m-%d %H:%M")

        return f"{self.flight_number} (departure: {departure}, status: {self.status})"