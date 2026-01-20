from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.airport_repository import AirportRepository
from flightmanagement.models.airport import Airport
from flightmanagement.db.db import transaction

class AirportService:

    def __init__(self, conn):
        self.conn = conn
        self.__airport_repository = AirportRepository(self.conn)

    def add_airport(self, code: str, name: str, city: str, country: str, region: str):
        with transaction(self.conn):
            airport = Airport(
                code=code,
                name=name,
                city=city,
                country=country,
                region=region
            )
            self.__airport_repository.add_airport(airport)        

    def update_airport(self, id: int, code: str, name: str, city: str, country: str, region: str):
        with transaction(self.conn):
            airport = Airport(
                id=id,
                code=code,
                name=name,
                city=city,
                country=country,
                region=region
            )
            self.__airport_repository.update_airport(airport)

    def delete_airport(self, id: int):
        with transaction(self.conn):
            self.__airport_repository.delete_airport(id)

    def get_airport_table(self) -> str:
        airports = self.__airport_repository.get_airport_list()

        if airports is None:
            return ""
        
        return self.get_results_view(airports)
    
    def search_airports(self, field_name: str, value) -> list[Airport] | None:
        return self.__airport_repository.search_on_field(field_name, value)

    def get_airport_choices(self) -> list:
        airports = self.__airport_repository.get_airport_list()
        
        airport_choices = []

        if airports:
            for airport in airports:
                airport_choices.append((airport.id, str(airport)))

        return airport_choices

    def get_airport_by_id(self, id: int):
        return self.__airport_repository.get_by_id(id)
    
    def get_results_view(self, airports: list[Airport]) -> str:
        if airports is None:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Airport ID",
            "Code",
            "Name",
            "City",
            "Country",
            "Region"
        ])
 
        # Populate table rows
        for airport in airports:
            table.add_row([airport.id, airport.code, airport.name, airport.city, airport.country, airport.region])
               
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
