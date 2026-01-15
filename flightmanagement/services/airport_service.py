from prettytable import PrettyTable
from flightmanagement.repositories.airport_repository import AirportRepository
from flightmanagement.models.airport import Airport
from flightmanagement.db.db import transaction

class AirportService:

    def __init__(self, conn):
        self.conn = conn
        self.__airport_repository = AirportRepository(self.conn)

    def add_airport(self, code: str, name: str, city: str, country: str, region: str):
        with transaction(self.conn):
            airport = Airport(None, code, name, city, country, region)
            self.__airport_repository.add_airport(airport)        

    def update_airport(self, id: int, code: str, name: str, city: str, country: str, region: str):
        with transaction(self.conn):
            airport = Airport(id, code, name, city, country, region)
            self.__airport_repository.update_airport(airport)

    def delete_airport(self, id: int):
        with transaction(self.conn):
            self.__airport_repository.delete_airport(id)

    def get_airport_table(self) -> str:
        airports = self.__airport_repository.get_airport_list()

        if airports is None:
            return ""
        
        return self.list_to_table(airports)
    
    def search_airports(self, field_name: str, value) -> str:
        results = self.__airport_repository.search_on_field(field_name, value)

        if results is None:
            return "No matching records."
        
        return self.list_to_table(results)

    def get_airport_choices(self) -> list:
        airports = self.__airport_repository.get_airport_list()
        
        airport_choices = []

        if airports:
            for airport in airports:
                airport_choices.append((airport.id, f"{airport.code} ({airport.name}, {airport.city}, {airport.country})"))

        return airport_choices

    def get_airport_by_id(self, id: int):
        return self.__airport_repository.get_by_id(id)
    
    def list_to_table(self, airports: list[Airport]) -> str:
        if airports is None:
            return ""
        
        table = PrettyTable([
            "Airport ID",
            "Code",
            "Name",
            "City",
            "Country",
            "Region"
        ])
        table.align = "l"

        for airport in airports:
            table.add_row([airport.id, airport.code, airport.name, airport.city, airport.country, airport.region])
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)
