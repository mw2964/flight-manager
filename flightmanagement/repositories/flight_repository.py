from datetime import datetime
from prettytable import PrettyTable
from flightmanagement.models.flight import Flight
from flightmanagement.db.db import DBOperations

class FlightRepository:

    def __init__(self):
        self.__db = DBOperations()
    
    def get_flight_by_id(self, id: int) -> Flight | None:

        result = self.__db.get_row_by_id("flight", id)

        if result:
            flight = Flight(
                id = result[0],
                flight_number = result[1],
                aircraft_id = result[2],
                origin_id = result[3],
                destination_id = result[4],
                pilot_id = result[5],
                copilot_id = result[6],
                departure_time_scheduled = datetime.strptime(result[7], '%Y-%m-%d %H:%M'),
                arrival_time_scheduled = datetime.strptime(result[8], '%Y-%m-%d %H:%M'),
                departure_time_actual = datetime.strptime(result[9], '%Y-%m-%d %H:%M') if result[9] else None,
                arrival_time_actual = datetime.strptime(result[10], '%Y-%m-%d %H:%M') if result[10] else None,
                status = result[11]
            )
            return flight

    def display_all(self) -> str:
        
        data = self.__db.select_all("flight")

        table = PrettyTable([
            "Flight ID",
            "Flight number",
            "Aircraft ID",
            "Origin ID",
            "Destination ID",
            "Pilot ID",
            "Copilot ID",
            "Departure time (scheduled)",
            "Arrival time (scheduled)",
            "Departure time (actual)",
            "Arrival time (actual)",
            "Status"
        ])        
        table.align = "l"

        if data:
            for row in data:
                table.add_row(row)

        return str(table)

    def get_flights_view(self):
        
        data = self.__db.select_flights_view()
        
        table = PrettyTable([
            "Flight ID",
            "Flight number",
            "Aircraft registration",
            "Aircraft type",
            "Origin",
            "Destination",
            "Scheduled departure",
            "Scheduled arrival",
            "Pilot",
            "Copilot",
            "Flight status"
        ])
        table.align = "l"

        if data:
            for row in data:
                table.add_row(row)
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)

    def get_flight_list(self) -> list | None:
        data = self.__db.select_flights_view()

        if not data:
            return None
        
        flights = []
        for row in data:
            flights.append((row[0], row[1], row[4], row[5], row[6], row[10]))

        return flights

    def add_flight(
            self,
            flight_number: str,
            aircraft_id: int,
            origin_id: int,
            destination_id: int,
            pilot_id: int | None,
            copilot_id: int | None,
            departure_date: str,
            departure_time: str,
            arrival_date: str,
            arrival_time: str
        ) -> bool:        
        
        try:
            # Add the new flight to the database
            data = {
                "flight_number": flight_number, 
                "aircraft_id": aircraft_id,
                "origin_id": origin_id, 
                "destination_id": destination_id,
                "pilot_id": pilot_id,
                "copilot_id": copilot_id,
                "departure_time_scheduled": departure_date + " " + departure_time,
                "arrival_time_scheduled": arrival_date + " " + arrival_time,
                "status": "Scheduled"
            }
            self.__db.insert_row("flight", data)

            return True
        except Exception as e:
            print(e)
            return False
    
    def update_flight(self, id: int, updates: dict): # Should be taking a flight object?
        self.__db.update_row("flight", id, updates)

    def delete_flight(self, id: int):
        self.__db.delete_row("flight", id)
