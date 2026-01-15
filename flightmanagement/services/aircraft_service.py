from prettytable import PrettyTable
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.db.db import transaction

class AircraftService:

    def __init__(self, conn):
        self.conn = conn
        self.__aircraft_repository = AircraftRepository(self.conn)

    def add_aircraft(self, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str):
        with transaction(self.conn):
            aircraft = Aircraft(None, registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
            self.__aircraft_repository.add_aircraft(aircraft)

    def update_aircraft(self, id: int, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str):
        with transaction(self.conn):
            aircraft = Aircraft(id, registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
            self.__aircraft_repository.update_aircraft(aircraft)

    def delete_aircraft(self, id: int):
        with transaction(self.conn):
            self.__aircraft_repository.delete_aircraft(id)

    def get_aircraft_table(self) -> str:
        aircraft = self.__aircraft_repository.get_aircraft_list()

        if aircraft is None:
            return ""
        
        return self.list_to_table(aircraft)
    
    def search_aircraft(self, field_name, value) -> str:
        results = self.__aircraft_repository.search_on_field(field_name, value)

        if results is None:
            return "No matching records."
        
        return self.list_to_table(results)
    
    def get_aircraft_choices(self) -> list:
        aircraft_list = self.__aircraft_repository.get_aircraft_list()
        
        aircraft_choices = []

        if aircraft_list:
            for aircraft in aircraft_list:
                aircraft_choices.append((aircraft.id, f"{aircraft.registration} ({aircraft.manufacturer} {aircraft.model})"))

        return aircraft_choices

    def get_aircraft_by_id(self, id: int):
        return self.__aircraft_repository.get_by_id(id)
    
    def list_to_table(self, aircraft: list[Aircraft]) -> str:
        if aircraft is None:
            return ""
        
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
        table.align = "l"

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
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)