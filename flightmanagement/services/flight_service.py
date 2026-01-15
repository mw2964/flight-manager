from datetime import datetime
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.repositories.airport_repository import AirportRepository
from flightmanagement.repositories.flight_repository import FlightRepository
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.flight import Flight
from flightmanagement.db.db import transaction

class FlightService:

    def __init__(self, conn):
        self.conn = conn
        self.__flight_repository = FlightRepository(self.conn)
        self.__aircraft_repository = AircraftRepository(self.conn)
        self.__airport_repository = AirportRepository(self.conn)
        self.__pilot_repository = PilotRepository(self.conn)

    def add_flight(self, flight_number: str, aircraft_id: int, origin_id: int, destination_id: int, pilot_id: int, copilot_id: int, departure_date: str, departure_time: str, arrival_date: str, arrival_time: str):
        with transaction(self.conn):
            flight = Flight(
                None,
                flight_number, 
                aircraft_id,
                origin_id, 
                destination_id,
                pilot_id,
                copilot_id,
                datetime.strptime(departure_date + " " + departure_time, "%Y-%m-%d %H:%M"),
                datetime.strptime(arrival_date + " " + arrival_time, "%Y-%m-%d %H:%M"),
                None,
                None,
                "Scheduled"
            )
        self.__flight_repository.add_flight(flight)

    def update_flight(self, id: int, flight_number: str, aircraft_id: int, origin_id: int, destination_id: int, pilot_id: int, copilot_id: int, departure_date_scheduled: str | None, departure_time_scheduled: str | None, arrival_date_scheduled: str | None, arrival_time_scheduled: str | None, departure_date_actual: str | None, departure_time_actual: str | None, arrival_date_actual: str | None, arrival_time_actual: str | None, status: str):
        with transaction(self.conn):
            flight = Flight(
                None,
                flight_number, 
                aircraft_id,
                origin_id, 
                destination_id,
                pilot_id,
                copilot_id,
                datetime.strptime(departure_date_scheduled, "%Y-%m-%d %H:%M") if departure_date_scheduled is not None else None,
                datetime.strptime(arrival_date_scheduled, "%Y-%m-%d %H:%M") if arrival_date_scheduled is not None else None,
                datetime.strptime(departure_date_actual, "%Y-%m-%d %H:%M") if departure_date_actual is not None else None,
                datetime.strptime(arrival_date_actual, "%Y-%m-%d %H:%M") if arrival_date_actual is not None else None,
                status
            )
            self.__flight_repository.update_flight(flight)

    def delete_flight(self, id: int):
        self.__flight_repository.delete_flight(id)

    def get_flight_table(self) -> str:
        flights = self.__flight_repository.get_flight_list()

        if flights is None:
            return ""
        
        return self.get_results_view(flights)

    def get_flight_by_id(self, id: int):
        return self.__flight_repository.get_by_id(id)

    def get_aircraft(self, aircraft_registration: str) -> int | None:
        aircraft = self.__aircraft_repository.get_by_registration(aircraft_registration)        
        if aircraft:
            return aircraft.id
        
    def get_airport(self, airport_code: str) -> int | None:
        airport = self.__airport_repository.get_by_code(airport_code)        
        if airport:
            return airport.id
    
    def search_flights(self, field_name: str, value) -> list[Flight] | None:
        return self.__flight_repository.search_on_field(field_name, value)

    def get_flight_choices(self, flight_number: str = "") -> list:
        flights = self.__flight_repository.get_flight_list()
        
        flight_choices = []

        if flights:
            for flight in flights:
                if flight_number == "" or flight.flight_number == flight_number:
                    flight_choices.append((flight.id, str(flight)))

        return flight_choices
    
    def get_results_view(self, flights: list[Flight]) -> str:
        if flights is None:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Flight ID",
            "Flight number",
            "Aircraft",
            "Origin",
            "Destination",
            "Pilot",
            "Copilot",
            "Departure (scheduled)",
            "Arrival (scheduled)",
            "Departure (actual)",
            "Arrival (actual)",
            "Status"
            ],
        )        
        
        # Populate table rows
        for flight in flights:
            table.add_row([
                flight.id,
                flight.flight_number,
                str(self.__aircraft_repository.get_by_id(flight.aircraft_id)).replace(" (", "\n("),
                str(self.__airport_repository.get_by_id(flight.origin_id)).replace(" (", "\n("),
                str(self.__airport_repository.get_by_id(flight.destination_id)).replace(" (", "\n("),
                self.__pilot_repository.get_by_id(flight.pilot_id) if flight.pilot_id else "",
                self.__pilot_repository.get_by_id(flight.copilot_id) if flight.copilot_id else "",
                datetime.strftime(flight.departure_time_scheduled, "%Y-%m-%d %H:%M") if flight.departure_time_scheduled else "",
                datetime.strftime(flight.arrival_time_scheduled, "%Y-%m-%d %H:%M") if flight.arrival_time_scheduled else "",
                datetime.strftime(flight.departure_time_actual, "%Y-%m-%d %H:%M") if flight.departure_time_actual else "",
                datetime.strftime(flight.arrival_time_actual, "%Y-%m-%d %H:%M") if flight.arrival_time_actual else "",
                flight.status
            ])

        # Set table formatting
        table.set_style(TableStyle.SINGLE_BORDER)
        table.align = "l"
        table.max_width = 20
        table.hrules = ALL
        table.vrules = NONE
        
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)