from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.pilot import Pilot
from flightmanagement.db.db import transaction

class PilotService:

    def __init__(self, conn, pilot_repository=None):
        self.conn = conn
        self.__pilot_repository = (
            pilot_repository or PilotRepository(self.conn)
        )

    def add_pilot(self, pilot: Pilot):
        with transaction(self.conn):
            self.__pilot_repository.insert_item(pilot)

    def update_pilot(self, pilot: Pilot):
        with transaction(self.conn):
            self.__pilot_repository.update_item(pilot)

    def delete_pilot(self, pilot: Pilot):
        if pilot.id is None:
            raise ValueError("Pilot to delete lacks an ID")
        with transaction(self.conn):
            self.__pilot_repository.delete_item(pilot)

    def get_pilot_table(self) -> str:
        pilots = self.__pilot_repository.get_pilot_list()

        if pilots is None:
            return ""
        
        return self.get_results_view(pilots)
    
    def get_pilot_choices(self) -> list:
        pilots = self.__pilot_repository.get_pilot_list()
        
        pilot_choices = []

        if pilots:
            for pilot in pilots:
                pilot_choices.append((pilot.id, str(pilot)))

        return pilot_choices
    
    def search_pilots(self, field_name: str, value) -> list[Pilot]:
        return self.__pilot_repository.search_on_field(field_name, value)

    def get_pilot_by_id(self, id: int):
        return self.__pilot_repository.get_item_by_id(id)
    
    def get_results_view(self, pilots: list[Pilot]) -> str:
        if pilots is None or len(pilots) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Pilot ID",
            "First name",
            "Family name"
        ])

        # Populate table rows
        for pilot in pilots:
            table.add_row([pilot.id, pilot.first_name, pilot.family_name])

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
    
    def display_record(self, pilot: Pilot) -> str:
        return f"\n> Pilot ID: {pilot.id}\n> First name: {pilot.first_name}\n> Family name: {pilot.family_name}"