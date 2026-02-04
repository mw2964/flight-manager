from datetime import datetime
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.repositories.location_repository import LocationRepository
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
        self.__location_repository = LocationRepository(self.conn)
        self.__pilot_repository = PilotRepository(self.conn)

    def add_flight(self, flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.insert_flight(flight)

    def update_flight(self,flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.update_flight(flight)

    def delete_flight(self, flight: Flight):
        if flight.flight_id is None:
            raise ValueError("Flight to delete lacks an ID")
        with transaction(self.conn):
            self.__flight_repository.delete_flight(flight)

    def get_flight_table(self) -> str:
        flights = self.__flight_repository.get_flight_list()

        if flights is None:
            return ""
        
        return self.get_results_view(flights)

    def get_flight_by_id(self, id: int) -> Flight | None:
        return self.__flight_repository.get_flight_by_id(id)

    def get_aircraft(self, aircraft_registration: str) -> int | None:
        aircraft = self.__aircraft_repository.get_aircraft_by_registration(aircraft_registration)        
        if aircraft:
            return aircraft.aircraft_id
        
    def get_location(self, location_code: str) -> int | None:
        location = self.__location_repository.get_location_by_code(location_code)        
        if location:
            return location.location_id
    
    def search_flights(self, field_name: str, value) -> list[Flight]:
        return self.__flight_repository.search_on_field(field_name, value)

    def get_flight_choices(self, flight_number: str = "") -> list:
        flights = self.__flight_repository.get_flight_list()
        
        flight_choices = []

        if flights:
            for flight in flights:
                if flight_number == "" or flight.flight_number == flight_number:                    
                    flight_choices.append((flight.flight_id, self.get_flight_summary(flight)))

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
            "Captain",
            "First officer",
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
                flight.flight_id,
                flight.flight_number,
                str(self.__aircraft_repository.get_aircraft_by_id(flight.aircraft_id)).replace(" (", "\n(") if flight.aircraft_id else None,
                str(self.__location_repository.get_location_by_id(flight.origin_location_id)).replace(" (", "\n("),
                str(self.__location_repository.get_location_by_id(flight.destination_location_id)).replace(" (", "\n("),
                self.__pilot_repository.get_pilot_by_id(flight.captain_id) if flight.captain_id else "",
                self.__pilot_repository.get_pilot_by_id(flight.first_officer_id) if flight.first_officer_id else "",
                f"{flight.scheduled_departure_date.strftime("%Y-%m-%d")} {flight.scheduled_departure_time.strftime("%H:%M")}",
                f"{flight.scheduled_arrival_date.strftime("%Y-%m-%d")} {flight.scheduled_arrival_time.strftime("%H:%M")}",
                f"{flight.confirmed_departure_date.strftime("%Y-%m-%d") if flight.confirmed_departure_date else None} {flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None}",
                f"{flight.confirmed_arrival_date.strftime("%Y-%m-%d") if flight.confirmed_arrival_date else None} {flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None}",
                flight.flight_status
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
        origin_location = self.__location_repository.get_location_by_id(flight.origin_location_id)        
        destination_location = self.__location_repository.get_location_by_id(flight.destination_location_id)

        origin_code = origin_location.iata_airport_code if origin_location is not None else ""
        destination_code = destination_location.iata_airport_code if destination_location is not None else ""

        departure = f"{flight.scheduled_departure_date.strftime("%Y-%m-%d")} {flight.scheduled_departure_time.strftime("%H:%M")}"

        spaces = 10 - len(flight.flight_number)

        return f"{flight.flight_number}{' ' * spaces}{origin_code} to {destination_code} | Departure: {departure} | Status: {flight.flight_status}"

    def assign_pilot_to_flight(self, flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.update_flight(flight)

    def add_relief_pilot(self, flight: Flight, staff_id: int):
        with transaction(self.conn):
            self.__flight_repository.insert_relief_pilot(flight, staff_id)

    def remove_relief_pilot(self, flight: Flight, staff_id: int):
        with transaction(self.conn):
            self.__flight_repository.delete_relief_pilot(flight, staff_id)

    def get_flight_relief_pilots(self, flight: Flight) -> list:
        if flight.flight_id is None:
            raise ValueError("Missing flight ID")
        return self.__flight_repository.get_relief_pilots_by_flight_id(flight.flight_id)

    def get_flight_relief_pilot_choices(self, flight: Flight) -> list:
        id_list = self.get_flight_relief_pilots(flight)

        relief_pilots = []
        if id_list:
            for id in id_list:
                pilot = self.__pilot_repository.get_pilot_by_id(id)
                relief_pilots.append((id, str(pilot)))

        return relief_pilots

    def get_available_pilot_choices(self, departure_time: datetime, arrival_time: datetime, unavailable_pilots: list = [], flight_id: int | None = None) -> list:
        
        # Get list of pilots that are available for the scheduled flight
        pilots = self.__flight_repository.get_available_pilots(departure_time, arrival_time, flight_id if flight_id else -1)
        
        pilot_choices = []
        if pilots:
            for pilot in pilots:
                # Skip pilots already assigned to the flight
                if pilot.staff_id in unavailable_pilots:
                    continue
                pilot_choices.append((pilot.staff_id, str(pilot)))

        return pilot_choices