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
    departure_time_actual: datetime | None
    arrival_time_scheduled: datetime | None
    arrival_time_actual: datetime | None
    status: str
