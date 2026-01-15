from datetime import datetime
from dataclasses import dataclass

@dataclass
class Flight:
    id: int | None
    flight_number: str
    aircraft_id: int
    origin_id: int
    destination_id: int
    pilot_id: int | None
    copilot_id: int | None
    departure_time_scheduled: datetime | None    
    arrival_time_scheduled: datetime | None
    departure_time_actual: datetime | None
    arrival_time_actual: datetime | None
    status: str

    def __str__(self):
        return f"{self.flight_number} ({self.origin_id} to {self.destination_id}, departure: {self.departure_time_scheduled}, status: {self.status})"