from prettytable import PrettyTable
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.pilot import Pilot
from flightmanagement.db.db import transaction

class PilotService:

    def __init__(self, conn):
        self.conn = conn
        self.__pilot_repository = PilotRepository(self.conn)

    def add_pilot(self, first_name: str, family_name: str):
        with transaction(self.conn):
            pilot = Pilot(None, first_name, family_name)
            self.__pilot_repository.add_pilot(pilot)

    def update_pilot(self, id: int, first_name: str, family_name: str):
        with transaction(self.conn):
            pilot = Pilot(id, first_name, family_name)
            self.__pilot_repository.update_pilot(pilot)

    def delete_pilot(self, id: int):
        with transaction(self.conn):
            self.__pilot_repository.delete_pilot(id)

    def get_pilot_table(self) -> str:
        pilots = self.__pilot_repository.get_pilot_list()

        if pilots is None:
            return ""
        
        return self.list_to_table(pilots)
    
    def get_pilot_choices(self) -> list:
        pilots = self.__pilot_repository.get_pilot_list()
        
        pilot_choices = []

        if pilots:
            for pilot in pilots:
                pilot_choices.append((pilot.id, f"{pilot.first_name} {pilot.family_name}"))

        return pilot_choices
    
    def search_pilots(self, field_name: str, value) -> str:
        results = self.__pilot_repository.search_on_field(field_name, value)

        if results is None:
            return "No matching records."
        
        return self.list_to_table(results)

    def get_pilot_by_id(self, id: int):
        return self.__pilot_repository.get_by_id(id)
    
    def list_to_table(self, pilots: list[Pilot]) -> str:
        if pilots is None:
            return ""
        
        table = PrettyTable([
            "Pilot ID",
            "First name",
            "Family name"
        ])
        table.align = "l"

        for pilot in pilots:
            table.add_row([pilot.id, pilot.first_name, pilot.family_name])
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)
    
    def display_record(self, pilot: Pilot) -> str:
        return f"\n> Pilot ID: {pilot.id}\n> First name: {pilot.first_name}\n> Family name: {pilot.family_name}"