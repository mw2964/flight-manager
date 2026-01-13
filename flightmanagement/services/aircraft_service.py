from flightmanagement.repositories.aircraft_repository import AircraftRepository

class AircraftService:

    def __init__(self):
        self.__aircraft_repository = AircraftRepository()

    def add_aircraft(self, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str):
        self.__aircraft_repository.add_aircraft(registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)

    def update_aircraft(self, id: int, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str):
        updates = {}
        if registration:
            updates["registration"] = registration
        if manufacturer_serial_no:
            updates["manufacturer_serial_no"] = manufacturer_serial_no
        if icao_hex:
            updates["icao_hex"] = icao_hex
        if manufacturer:
            updates["manufacturer"] = manufacturer
        if model:
            updates["model"] = model
        if icao_type:
            updates["icao_type"] = icao_type
        if status:
            updates["status"] = status
        
        self.__aircraft_repository.update_aircraft(id, updates)

    def delete_aircraft(self, id: int):
        self.__aircraft_repository.delete_aircraft(id)

    def get_aircraft_list(self) -> str:
        return self.__aircraft_repository.display_all()
    
    def search_aircraft(self, field_name, value) -> str:
        return self.__aircraft_repository.search_aircraft(field_name, value)
    
    def get_aircraft_choices(self) -> list:
        aircraft_list = self.__aircraft_repository.get_aircraft_list()
        
        aircraft_choices = []

        if aircraft_list:
            for aircraft in aircraft_list:
                aircraft_choices.append((aircraft.id, f"{aircraft.registration} ({aircraft.manufacturer} {aircraft.model})"))

        return aircraft_choices

    def get_aircraft_by_id(self, id: int):
        return self.__aircraft_repository.get_aircraft_by_id(id)