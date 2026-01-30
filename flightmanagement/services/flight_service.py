from datetime import datetime
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.repositories.airport_repository import AirportRepository
from flightmanagement.repositories.flight_repository import FlightRepository
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.flight import Flight
from flightmanagement.db.db import transaction

class FlightService:

    def __init__(self, conn, flight_repository=None):
        self.conn = conn
        self.__flight_repository = (
            flight_repository or FlightRepository(self.conn)
        )
        self.__aircraft_repository = AircraftRepository(self.conn)
        self.__airport_repository = AirportRepository(self.conn)
        self.__pilot_repository = PilotRepository(self.conn)

    def add_flight(self, flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.insert_item(flight)

    def update_flight(self,flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.update_item(flight)

    def delete_flight(self, flight: Flight):
        if flight.id is None:
            raise ValueError("Flight to delete lacks an ID")
        with transaction(self.conn):
            self.__flight_repository.delete_item(flight)

    def get_flight_table(self) -> str:
        flights = self.__flight_repository.get_flight_list()

        if flights is None:
            return ""
        
        return self.get_results_view(flights)

    def get_flight_by_id(self, id: int) -> Flight | None:
        return self.__flight_repository.get_item_by_id(id)

    def get_aircraft(self, aircraft_registration: str) -> int | None:
        aircraft = self.__aircraft_repository.get_item_by_registration(aircraft_registration)        
        if aircraft:
            return aircraft.id
        
    def get_airport(self, airport_code: str) -> int | None:
        airport = self.__airport_repository.get_item_by_code(airport_code)        
        if airport:
            return airport.id
    
    def search_flights(self, field_name: str, value) -> list[Flight]:
        return self.__flight_repository.search_on_field(field_name, value)

    def get_flight_choices(self, flight_number: str = "") -> list:
        flights = self.__flight_repository.get_flight_list()
        
        flight_choices = []

        if flights:
            for flight in flights:
                if flight_number == "" or flight.flight_number == flight_number:                    
                    flight_choices.append((flight.id, self.get_flight_summary(flight)))

        return flight_choices
    
    def get_results_view(self, flights: list[Flight]) -> str:
        if flights is None or len(flights) == 0:
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
                str(self.__aircraft_repository.get_item_by_id(flight.aircraft_id)).replace(" (", "\n("),
                str(self.__airport_repository.get_item_by_id(flight.origin_id)).replace(" (", "\n("),
                str(self.__airport_repository.get_item_by_id(flight.destination_id)).replace(" (", "\n("),
                self.__pilot_repository.get_item_by_id(flight.pilot_id) if flight.pilot_id else "",
                self.__pilot_repository.get_item_by_id(flight.copilot_id) if flight.copilot_id else "",
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
    
    def get_flight_summary(self, flight: Flight) -> str:
        origin_airport = self.__airport_repository.get_item_by_id(flight.origin_id)        
        destination_airport = self.__airport_repository.get_item_by_id(flight.destination_id)

        origin_code = origin_airport.code if origin_airport is not None else ""
        destination_code = destination_airport.code if destination_airport is not None else ""

        if flight.departure_time_scheduled is None:
            departure = ""
        else:
            departure = datetime.strftime(flight.departure_time_scheduled, "%Y-%m-%d %H:%M")

        spaces = 10 - len(flight.flight_number)

        return f"{flight.flight_number}{' ' * spaces}{origin_code} to {destination_code} | Departure: {departure} | Status: {flight.status}"

    def assign_pilot_to_flight(self, flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.update_item(flight)

    def get_available_pilot_choices(self, departure_time: datetime, arrival_time: datetime, flight_id: int | None = None, pilot_id: int | None = None) -> list:
        pilots = self.__flight_repository.get_available_pilots(departure_time, arrival_time, flight_id if flight_id else -1)
        
        pilot_choices = []

        if pilots:
            for pilot in pilots:
                if pilot.id != pilot_id:
                    pilot_choices.append((pilot.id, str(pilot)))

        return pilot_choices