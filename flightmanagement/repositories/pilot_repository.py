from prettytable import PrettyTable
from flightmanagement.models.pilot import Pilot
from flightmanagement.db.db import DBOperations

class PilotRepository:

    def __init__(self):
        self.__db = DBOperations()

    def get_pilot_by_id(self, id: int) -> Pilot | None:
        
        result = self.__db.get_row_by_id("pilot", id)
        
        if result:
            pilot = Pilot(
                id = result[0],
                first_name = result[1],
                family_name = result[2]
            )
            return pilot

    def add_pilot(self, first_name: str, family_name: str) -> bool:        
        
        try:
            # Add the new pilot to the database
            data = {"first_name": first_name, "family_name": family_name}
            self.__db.insert_row("pilot", data)
            return True
        except Exception as e:
            print(e)
            return False

    def get_pilot_list(self) -> list[Pilot] | None:
        data = self.__db.select_all("pilot")

        if not data:
            return None
        
        pilots = []
        for row in data:
            pilots.append(Pilot(row[0], row[1], row[2]))

        return pilots

    def update_pilot(self, id: int, updates: dict): # Should be taking a pilot object?
        self.__db.update_row("pilot", id, updates)
    
    def delete_pilot(self, id: int):
        self.__db.delete_row("pilot", id)
    
    def search_pilots(self, field_name: str, value) -> str:
        result_id = self.__db.search_data("pilot", field_name, value)
        
        if result_id:
            pilot = self.get_pilot_by_id(result_id)
            if pilot:
                return "\nMatch found:\n" + self.display_record(pilot)
            else:
                return "\nNo matching records"
        else:
            return "\nNo matching records"

    def display_all(self) -> str:
        
        data = self.__db.select_all("pilot")

        table = PrettyTable([
            "Pilot ID",
            "First name",
            "Family name"
        ])
        table.align = "l"

        if data:
            for row in data:
                table.add_row(row)
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)
    
    def display_record(self, pilot: Pilot) -> str:
        return f"\n> Pilot ID: {pilot.id}\n> First name: {pilot.first_name}\n> Family name: {pilot.family_name}"
    