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

    def get_pilot(self, flight: Flight):
        pass

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
    
        return str(table)

    '''
    def add_flight(self, flight_number: str, aircraft: str, origin: str, destination: str, pilot_id: int, copilot_id: int, departure_date: str, departure_time: str, arrival_date: str, arrival_time: str) -> bool:        
        
        try:
            # Add the new aircraft to the database
            data = {
                "registration": registration, 
                "manufacturer_serial_no": manufacturer_serial_no,
                "icao_hex": icao_hex, 
                "manufacturer": manufacturer,
                "model": model,
                "icao_type": icao_type,
                "status": status
            }
            self.__db.insert_row("aircraft", data)

            # Refresh the repository list
            self.__load_aircraft()

            return True
        except Exception as e:
            print(e)
            return False
    '''
            
    def delete_flight(self, id: int):
        self.__db.delete_row("flight", id)
