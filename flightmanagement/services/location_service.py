import pandas as pd
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.error import MissingData, DependentRecords, DuplicateRecord, InvalidData, ForeignKeyDependencyViolation, ForeignKeyInvalidViolation, UniqueConstraintViolation, CheckConstraintViolation, MissingNotNullViolation
from flightmanagement.repositories.location_repository import LocationRepository
from flightmanagement.models.location import Location
from flightmanagement.db.db import transaction

class LocationService:

    def __init__(self, conn, location_repository = None):
        self.conn = conn
        self.__location_repository = (
            location_repository or LocationRepository(self.conn)
        )

    def add_location(self, location: Location) -> int:
        try:
            with transaction(self.conn):
                return self.__location_repository.insert_location(location)
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def update_location(self, location: Location):
        try: 
            with transaction(self.conn):
                self.__location_repository.update_location(location)
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def delete_location(self, location: Location):
        if location.location_id is None:
            raise ValueError("Location to delete lacks an ID")
        
        try:
            with transaction(self.conn):
                self.__location_repository.delete_location(location)
        except ForeignKeyDependencyViolation as e:
            raise DependentRecords(e)

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

    def get_airport_terminal_choices(self, location_id: int) -> list:
        terminals = self.__location_repository.get_location_terminals(location_id)

        terminal_choices = []
        if terminals:
            for terminal in terminals:
                terminal_choices.append((terminal.terminal_id, terminal.terminal_name))
        
        return terminal_choices
    
    def get_terminal_gate_choices(self, terminal_id: int) -> list:
        gates = self.__location_repository.get_terminal_gates(terminal_id)

        gate_choices = []
        if gates:
            for gate in gates:
                gate_choices.append((gate.gate_id, gate.gate_number))
        
        return gate_choices

    def get_airport_gate_choices(self, location_id: int) -> list:        
        terminals = self.__location_repository.get_location_terminals(location_id)
        
        gate_choices = []
        if terminals:
            for terminal in terminals:
                gates = self.__location_repository.get_terminal_gates(terminal.terminal_id)
                for gate in gates:
                    gate_choices.append((gate.gate_id, f"{terminal.terminal_name} -> {gate.gate_number}"))
        
        return gate_choices

    def get_location_by_id(self, id: int):
        return self.__location_repository.get_location_by_id(id)

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
                location.iata_airport_code if location.iata_airport_code else '',
                location.icao_location_code if location.icao_location_code else '',
                location.location_name,
                location.town_or_city if location.town_or_city else '',
                location.state_or_county if location.state_or_county else '',
                location.country,
                location.geographic_region if location.geographic_region else '',
                location.decimal_latitude if location.decimal_latitude else '',
                location.decimal_longitude if location.decimal_longitude else ''
            ])
        return self._format_table(table)
    
    def get_results_view_pandas(self, locations: list[Location]) -> str:                
        
        if locations is None or len(locations) == 0:
            return ""
        
        df = pd.DataFrame.from_records([location.to_dict() for location in locations])        

        return df.to_string()

    def _format_table(self, table: PrettyTable) -> str:

        # Set table formatting
        table.set_style(TableStyle.SINGLE_BORDER)
        table.align = "l"
        table.max_width = 20
        table.hrules = ALL
        table.vrules = NONE
        
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return indented_table