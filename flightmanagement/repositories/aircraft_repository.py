from prettytable import PrettyTable
from typing import Optional
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.db.db import DBOperations

class AircraftRepository:

    def __init__(self):
        self.__db = DBOperations()

    def get_aircraft_by_id(self, id: int):

        result = self.__db.get_row_by_id("aircraft", id)
        
        if result:
            aircraft = Aircraft(
                id = result[0],
                registration = result[1],
                manufacturer_serial_no = result[2],
                icao_hex = result[3],
                manufacturer = result[4],
                model = result[5],
                icao_type = result[6],
                status = result[7]
            )
            return aircraft

    def get_aircraft_by_registration(self, registration: str) -> Aircraft | None:

        id = self.__db.search_data("aircraft", "registration", registration)
        
        if id:
            return self.get_aircraft_by_id(id)

    def get_aircraft_list(self) -> list[Aircraft] | None:
        data = self.__db.select_all("aircraft")

        if not data:
            return None
        
        aircraft = []
        for row in data:
            aircraft.append(Aircraft(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        return aircraft

    def add_aircraft(self, registration: str, manufacturer_serial_no: int, icao_hex: str, manufacturer: str, model: str, icao_type: str, status: str) -> bool:        
        
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

            return True
        except Exception as e:
            print(e)
            return False

    def update_aircraft(self, id: int, updates: dict):
        self.__db.update_row("aircraft", id, updates)
    
    def delete_aircraft(self, id: int):
        self.__db.delete_row("aircraft", id)
    
    def search_aircraft(self, field_name: str, value) -> str:
        result_id = self.__db.search_data("aircraft", field_name, value)
        
        if result_id is not None:
            aircraft = self.get_aircraft_by_id(result_id)
            if aircraft is not None:
                return "\nMatch found:\n" + self.display_record(aircraft)
            else:
                return "\nNo matching records"
        else:
            return "\nNo matching records"

    def display_all(self) -> str:
        
        data = self.__db.select_all("aircraft")

        table = PrettyTable(["Aircraft ID", "Registration", "Manufacturer serial no", "ICAO hex code", "Manufacturer", "Model", "ICAO type", "Status"])
        table.align = "l"

        if data:
            for row in data:
                table.add_row(row)
    
        return str(table)
    
    def display_record(self, aircraft: Aircraft) -> str:
        record_string = f"""
> Aircraft ID: {aircraft.id}
> Registration: {aircraft.registration}
> Manufacturer serial no: {aircraft.manufacturer_serial_no}
> ICAO hex code: {aircraft.icao_hex}
> Manufacturer: {aircraft.manufacturer}
> Model: {aircraft.model}
> ICAO type: {aircraft.icao_type}
> Status: {aircraft.status}
        """
        return record_string