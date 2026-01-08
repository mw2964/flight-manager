from datetime import datetime
from prettytable import PrettyTable
from typing import Optional
from flightmanagement.models.flight import Flight
from flightmanagement.models.pilot import Pilot
from flightmanagement.models.airport import Airport
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.db.db import DBOperations

class FlightRepository:

    def __init__(self):
        self.__db = DBOperations()
        self.__flights: list[Flight] = self.__get_all_flights()
    
    def __str__(self) -> str:
        flight_string = ""
        for flight in self.__flights:
            flight_string += str(flight) + "\n"
        return flight_string

    def __get_all_flights(self) -> list[Flight]:
        db = DBOperations()
        rows = db.select_all("flight")

        flights: list[Flight] = []

        if rows != None:
            for row in rows:
                flight = Flight(
                    id = row[0],
                    flight_number = row[1],
                    aircraft_id = row[2],
                    origin_id = row[3],
                    destination_id = row[4],
                    pilot_id = row[5],
                    copilot_id = row[6],
                    departure_time_scheduled = datetime.strptime(row[7], '%Y-%m-%d %H:%M'),
                    arrival_time_scheduled = datetime.strptime(row[8], '%Y-%m-%d %H:%M'),
                    departure_time_actual = datetime.strptime(row[9], '%Y-%m-%d %H:%M') if row[9] != None else None,
                    arrival_time_actual = datetime.strptime(row[10], '%Y-%m-%d %H:%M') if row[10] != None else None,
                    status = row[11]
                )
                flights.append(flight)
        
        return flights
 
    def display_all(self) -> str:
        
        table = PrettyTable(["Flight ID", "Flight number", "Aircraft ID", "Origin ID", "Destination ID"])

        for flight in self.__flights:
            table.add_row([flight.id, flight.flight_number, flight.aircraft_id, flight.origin_id, flight.destination_id])
    
        table.align = "l"

        return str(table)

    def get_pilot(self, flight: Flight):
        pass

class PilotRepository:

    def __init__(self):
        self.__db = DBOperations()
        self.__pilots: list[Pilot] = []
        self.__load_pilots()

    def __str__(self) -> str:
        pilot_string = ""
        for pilot in self.__pilots:
            pilot_string += str(pilot) + "\n"
        return pilot_string

    def __load_pilots(self) -> None:
        db = DBOperations()
        rows = db.select_all("pilot")

        self.__pilots = []
        if rows != None:
            for row in rows:
                pilot = Pilot(
                    id = row[0],
                    first_name = row[1],
                    family_name = row[2]
                )
                self.__pilots.append(pilot)
    
    def __get_pilot_by_id(self, id: int) -> Optional[Pilot]:
        for pilot in self.__pilots:
            if pilot.id == id:
                return pilot

    def add_pilot(self, first_name: str, family_name: str) -> bool:        
        
        try:
            # Add the new pilot to the database
            data = {"first_name": first_name, "family_name": family_name}
            self.__db.insert_data("pilot", data)

            # Refresh the repository list
            self.__load_pilots()

            return True
        except Exception as e:
            print(e)
            return False

    def update_pilot(self, id: int, updates: dict):
        self.__db.update_row("pilot", id, updates)
        self.__load_pilots()
    
    def delete_pilot(self, id: int):
        self.__db.delete_row("pilot", id)
        self.__load_pilots()
    
    def search_pilots(self, field_name: str, value) -> str:
        result_id = self.__db.search_data("pilot", field_name, value)
        
        if result_id is not None:
            pilot = self.__get_pilot_by_id(result_id)
            if pilot is not None:
                return "\nMatch found:\n" + self.display_record(pilot)
            else:
                return "\nNo matching records"
        else:
            return "\nNo matching records"

    def display_all(self) -> str:
        
        table = PrettyTable(["Pilot ID", "First name", "Family name"])
        table.align = "l"

        for pilot in self.__pilots:
            table.add_row([pilot.id, pilot.first_name, pilot.family_name])
    
        return str(table)
    
    def display_record(self, pilot: Pilot) -> str:
        return f"\n> Pilot ID: {pilot.id}\n> First name: {pilot.first_name}\n> Family name: {pilot.family_name}\n"
    
class AirportRepository:

    def __init__(self):
        self.__db = DBOperations()
        self.__airports: list[Airport] = []
        self.__load_airports()

    def __str__(self) -> str:
        airport_string = ""
        for airport in self.__airports:
            airport_string += str(airport) + "\n"
        return airport_string

    def __load_airports(self) -> None:
        db = DBOperations()
        rows = db.select_all("airport")

        self.__airports = []
        if rows != None:
            for row in rows:
                airport = Airport(
                    id = row[0],
                    code = row[1],
                    name = row[2],
                    city = row[3],
                    country = row[4],
                    region = row[5]
                )
                self.__airports.append(airport)
    
    def __get_airport_by_id(self, id: int) -> Optional[Airport]:
        for airport in self.__airports:
            if airport.id == id:
                return airport

    def add_airport(self, code: str, name: str, city: str, country: str, region: str) -> bool:        
        
        try:
            # Add the new airport to the database
            data = {
                "code": code, 
                "name": name,
                "city": city, 
                "country": country,
                "region": region
            }
            self.__db.insert_data("airport", data)

            # Refresh the repository list
            self.__load_airports()

            return True
        except Exception as e:
            print(e)
            return False

    def update_airport(self, id: int, updates: dict):
        self.__db.update_row("airport", id, updates)
        self.__load_airports()
    
    def delete_airport(self, id: int):
        self.__db.delete_row("airport", id)
        self.__load_airports()
    
    def search_airports(self, field_name: str, value) -> str:
        result_id = self.__db.search_data("airport", field_name, value)
        
        if result_id is not None:
            airport = self.__get_airport_by_id(result_id)
            if airport is not None:
                return "\nMatch found:\n" + self.display_record(airport)
            else:
                return "\nNo matching records"
        else:
            return "\nNo matching records"

    def display_all(self) -> str:
        
        table = PrettyTable(["Airport ID", "Code", "Name", "City", "Country", "Region"])
        table.align = "l"

        for airport in self.__airports:
            table.add_row([airport.id, airport.code, airport.name, airport.city, airport.country, airport.region])
    
        return str(table)
    
    def display_record(self, airport: Airport) -> str:
        record_string = f"""
> Airport ID: {airport.id}
> Code: {airport.code}
> Name: {airport.name}
> City: {airport.city}
> Country: {airport.country}
> Region: {airport.region}
        """
        return record_string