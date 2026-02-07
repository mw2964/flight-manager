from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.error import ConstraintViolation, ForeignKeyDependencyViolation
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.db.db import transaction

class AircraftService:

    def __init__(self, conn, aircraft_repository = None):
        self.conn = conn
        self.__aircraft_repository = (
            aircraft_repository or AircraftRepository(self.conn)
        )

    def add_aircraft(self, aircraft: Aircraft) -> int:
        with transaction(self.conn):
            return self.__aircraft_repository.insert_aircraft(aircraft)

    def update_aircraft(self, aircraft: Aircraft):
        with transaction(self.conn):
            self.__aircraft_repository.update_aircraft(aircraft)

    def delete_aircraft(self, aircraft: Aircraft):
        if aircraft.aircraft_id is None:
            raise ValueError("Aircraft to delete lacks an ID")
        
        try:
            with transaction(self.conn):
                self.__aircraft_repository.delete_aircraft(aircraft)
        except ForeignKeyDependencyViolation as e:
            raise ConstraintViolation(e)

    def get_aircraft_table(self) -> str:
        aircraft = self.__aircraft_repository.get_aircraft_list()
        return self.get_results_view(aircraft)
    
    def search_aircraft(self, field_name: str, value) -> list:
        return self.__aircraft_repository.search_aircraft_on_field(field_name, value)
    
    def get_aircraft_choices(self) -> list:
        aircraft_list = self.__aircraft_repository.get_aircraft_list()
        
        aircraft_choices = []

        if aircraft_list:
            for aircraft in aircraft_list:                
                aircraft_type = self.__aircraft_repository.get_aircraft_type_by_id(aircraft.aircraft_type_id)                               
                aircraft_type_str = f"({aircraft_type.manufacturer} {aircraft_type.model}) " if aircraft_type else ""
                aircraft_choices.append((aircraft.aircraft_id, f"{aircraft.registration} {aircraft_type_str}- {aircraft.aircraft_status}"))

        return aircraft_choices

    def get_aircraft_type_choices(self) -> list:
        aircraft_type_list = self.__aircraft_repository.get_aircraft_type_list()
        
        aircraft_type_choices = []

        if aircraft_type_list:
            for aircraft_type in aircraft_type_list:
                aircraft_type_choices.append((aircraft_type["aircraft_type_id"], f"{aircraft_type['manufacturer']} {aircraft_type["model"]}"))

        return aircraft_type_choices

    def get_aircraft_by_id(self, id: int):
        return self.__aircraft_repository.get_aircraft_by_id(id)
    
    def get_results_view(self, aircraft: list[Aircraft]) -> str:
        if aircraft is None or len(aircraft) == 0:
            return ""
    
        # Initialise the table
        table = PrettyTable([
            "Aircraft ID",
            "Registration",
            "Manufacturer serial no",
            "ICAO hex code",
            "Manufacturer",
            "Model",
            "ICAO type",
            "Status"
        ])

        # Populate table rows
        for item in aircraft:
            aircraft_type = self.__aircraft_repository.get_aircraft_type_by_id(item.aircraft_type_id)
            table.add_row([
                item.aircraft_id,
                item.registration,
                item.manufacturer_serial_no,
                item.icao_hex,
                aircraft_type.manufacturer if aircraft_type else "",
                aircraft_type.model if aircraft_type else "",
                aircraft_type.icao_type if aircraft_type else "",
                item.aircraft_status
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
    