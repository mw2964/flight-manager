from datetime import datetime

class Flight:

    def __init__(
        self,
        id: int,
        flight_number: str,
        aircraft_id: int,
        origin_id: int,
        destination_id: int,
        pilot_id: int | None,
        copilot_id: int | None,
        departure_time_scheduled: datetime | None,
        departure_time_actual: datetime | None,
        arrival_time_scheduled: datetime | None,
        arrival_time_actual: datetime | None,
        status: str,
    ) -> None:
        
        self.__id: int = id
        self.__flight_number: str = flight_number
        self.__aircraft_id: int = aircraft_id
        self.__origin_id: int = origin_id
        self.__destination_id: int = destination_id
        self.__pilot_id: int | None = pilot_id
        self.__copilot_id: int | None = copilot_id
        self.__departure_time_scheduled: datetime | None = departure_time_scheduled
        self.__departure_time_actual: datetime | None = departure_time_actual
        self.__arrival_time_scheduled: datetime | None = arrival_time_scheduled
        self.__arrival_time_actual: datetime | None = arrival_time_actual
        self.__status: str = status

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        if value is not None and value < 0:
            raise ValueError("id must be a non-negative integer or None.")
        self.__id = value

    @property
    def flight_number(self) -> str:
        return self.__flight_number

    @flight_number.setter
    def flight_number(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("flight_number must be a non-empty string.")
        self.__flight_number = value
    
    @property
    def aircraft_id(self) -> int:
        return self.__aircraft_id

    @aircraft_id.setter
    def aircraft_id(self, value: int) -> None:
        if value is not None and value < 0:
            raise ValueError("aircraft_id must be a non-negative integer or None.")
        self.__aircraft_id = value

    @property
    def origin_id(self) -> int:
        return self.__origin_id

    @origin_id.setter
    def origin_id(self, value: int) -> None:
        if value is not None and value < 0:
            raise ValueError("origin_id must be a non-negative integer or None.")
        self.__origin_id = value

    @property
    def destination_id(self) -> int:
        return self.__destination_id

    @destination_id.setter
    def destination_id(self, value: int) -> None:
        if value is not None and value < 0:
            raise ValueError("destination_id must be a non-negative integer or None.")
        self.__destination_id = value

    @property
    def pilot_id(self) -> int | None:
        return self.__pilot_id

    @pilot_id.setter
    def pilot_id(self, value: int | None) -> None:
        if value is not None and value < 0:
            raise ValueError("pilot_id must be a non-negative integer or None.")
        self.__pilot_id = value

    @property
    def copilot_id(self) -> int | None:
        return self.__copilot_id

    @copilot_id.setter
    def copilot_id(self, value: int | None) -> None:
        if value is not None and value < 0:
            raise ValueError("copilot_id must be a non-negative integer or None.")
        self.__copilot_id = value

    @property
    def departure_time_scheduled(self) -> datetime | None:
        return self.__departure_time_scheduled

    @departure_time_scheduled.setter
    def departure_time_scheduled(self, value: datetime | None) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError("departure_time_scheduled must be a datetime or None.")
        self.__departure_time_scheduled = value

    @property
    def departure_time_actual(self) -> datetime | None:
        return self.__departure_time_actual

    @departure_time_actual.setter
    def departure_time_actual(self, value: datetime | None) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError("departure_time_actual must be a datetime or None.")
        self.__departure_time_actual = value

    @property
    def arrival_time_scheduled(self) -> datetime | None:
        return self.__arrival_time_scheduled

    @arrival_time_scheduled.setter
    def arrival_time_scheduled(self, value: datetime | None) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError("arrival_time_scheduled must be a datetime or None.")
        self.__arrival_time_scheduled = value

    @property
    def arrival_time_actual(self) -> datetime | None:
        return self.__arrival_time_actual

    @arrival_time_actual.setter
    def arrival_time_actual(self, value: datetime | None) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError("arrival_time_actual must be a datetime or None.")
        self.__arrival_time_actual = value

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, value: str) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("status must be a string or None.")
        self.__status = value

    def __str__(self):
        flight_string = f"{self.id}. {self.flight_number}"
        if self.departure_time_scheduled is not None:
            flight_string += f" (dept. {datetime.strftime(self.departure_time_scheduled, "%Y-%m-%d %H:%M")})"
        return flight_string