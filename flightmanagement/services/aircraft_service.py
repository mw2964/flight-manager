from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.db.db import transaction

class AircraftService:

    def __init__(self, conn):
        self.conn = conn
        self.__aircraft_repository = AircraftRepository(self.conn)

    def add_aircraft(self, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str):
        with transaction(self.conn):
            aircraft = Aircraft(
                id=None,
                registration=registration,
                manufacturer_serial_no=manufacturer_serial_no,
                icao_hex=icao_hex,
                manufacturer=manufacturer,
                model=model,
                icao_type=icao_type,
                status=status
            )
            self.__aircraft_repository.add_aircraft(aircraft)

    def update_aircraft(self, id: int, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str):
        with transaction(self.conn):
            aircraft = Aircraft(
                id=id,
                registration=registration,
                manufacturer_serial_no=manufacturer_serial_no,
                icao_hex=icao_hex,
                manufacturer=manufacturer,
                model=model,
                icao_type=icao_type,
                status=status
            )
            self.__aircraft_repository.update_aircraft(aircraft)

    def delete_aircraft(self, id: int):
        with transaction(self.conn):
            self.__aircraft_repository.delete_aircraft(id)

    def get_aircraft_table(self) -> str:
        aircraft = self.__aircraft_repository.get_aircraft_list()
        return self.get_results_view(aircraft)
    
    def search_aircraft(self, field_name, value) -> list[Aircraft]:
        return self.__aircraft_repository.search_on_field(field_name, value)
    
    def get_aircraft_choices(self) -> list:
        aircraft_list = self.__aircraft_repository.get_aircraft_list()
        
        aircraft_choices = []

        if aircraft_list:
            for aircraft in aircraft_list:
                aircraft_choices.append((aircraft.id, str(aircraft) + " - " + aircraft.status))

        return aircraft_choices

    def get_aircraft_by_id(self, id: int):
        return self.__aircraft_repository.get_by_id(id)
    
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
            table.add_row([
                item.id,
                item.registration,
                item.manufacturer_serial_no,
                item.icao_hex,
                item.manufacturer,
                item.model,
                item.icao_type,
                item.status
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