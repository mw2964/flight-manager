from flightmanagement.repositories.pilot_repository import PilotRepository

class PilotService:

    def __init__(self):
        self.__pilot_repository = PilotRepository()

    def add_pilot(self, first_name: str, family_name: str):
        self.__pilot_repository.add_pilot(first_name, family_name)

    def update_pilot(self, id: int, first_name: str, family_name: str):
        updates = {}
        if first_name:
            updates["first_name"] = first_name
        if family_name:
            updates["family_name"] = family_name
        
        self.__pilot_repository.update_pilot(id, updates)

    def delete_pilot(self, id: int):
        self.__pilot_repository.delete_pilot(id)

    def get_pilot_list(self) -> str:
        return self.__pilot_repository.display_all()
    
    def search_pilots(self, field_name: str, value) -> str:
        return self.__pilot_repository.search_pilots(field_name, value)