import pandas as pd
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.location_repository import LocationRepository
from flightmanagement.models.location import Location
from flightmanagement.db.db import transaction

class LocationService:

    def __init__(self, conn, location_repository=None):
        self.conn = conn
        self.__location_repository = (
            location_repository or LocationRepository(self.conn)
        )

    def add_location(self, location: Location):
        with transaction(self.conn):
            self.__location_repository.insert_item(location)        

    def update_location(self, location: Location):
        with transaction(self.conn):
            self.__location_repository.update_item(location)

    def delete_location(self, location: Location):
        if location.location_id is None:
            raise ValueError("Location to delete lacks an ID")
        with transaction(self.conn):
            self.__location_repository.delete_item(location)

    def get_location_table(self) -> str:
        locations = self.__location_repository.get_location_list()

        if locations is None:
            return ""
        
        return self.get_results_view(locations)
    
    def search_locations(self, field_name: str, value) -> list[Location]:
        return self.__location_repository.search_on_field(field_name, value)

    def get_location_choices(self) -> list:
        locations = self.__location_repository.get_location_list()
        
        location_choices = []

        if locations:
            for location in locations:
                location_choices.append((location.location_id, str(location)))

        return location_choices

    def get_location_by_id(self, id: int):
        return self.__location_repository.get_item_by_id(id)
    
    def get_results_view(self, locations: list[Location]) -> str:
        if locations is None or len(locations) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "ID",
            "Type",
            "Airport code",
            "Location code",
            "Name",
            "Town/city",
            "State/county/province",
            "Country",
            "Region",
            "Lat",
            "Long"
        ])
 
        # Populate table rows
        for location in locations:
            table.add_row([
                location.location_id,
                location.location_type,
                location.iata_airport_code,
                location.icao_location_code,
                location.location_name,
                location.town_or_city,
                location.state_or_county,
                location.country,
                location.geographic_region,
                location.decimal_latitude,
                location.decimal_longitude
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
    
    def get_results_view_pandas(self, locations: list[Location]) -> str:                
        
        if locations is None or len(locations) == 0:
            return ""
        
        df = pd.DataFrame.from_records([location.to_dict() for location in locations])        

        return df.to_string()
