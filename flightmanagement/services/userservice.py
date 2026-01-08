from flightmanagement.repositories.repositories import FlightRepository, PilotRepository, AirportRepository
from flightmanagement.db.db import DBOperations

class UserService:

    def __init__(self):
        self.__flight_repository = FlightRepository()
        self.__pilot_repository = PilotRepository()
        self.__airport_repository = AirportRepository()
    
    # Flight functions

    def get_flight_list(self) -> str:
        return f"\n{self.__flight_repository}"
    
    def get_all_flight_details(self) -> str:
        return self.__flight_repository.display_all()

    # Pilot functions

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
    
    # Airport functions

    def add_airport(self, code: str, name: str, city: str, country: str, region: str):
        self.__airport_repository.add_airport(code, name, city, country, region)

    def update_airport(self, id, code, name, city, country, region):
        updates = {}
        if code:
            updates["code"] = code
        if name:
            updates["name"] = name
        if city:
            updates["city"] = city
        if country:
            updates["country"] = country
        if region:
            updates["region"] = region
        
        self.__airport_repository.update_airport(id, updates)

    def delete_airport(self, id: int):
        self.__airport_repository.delete_airport(id)

    def get_airport_list(self) -> str:
        return self.__airport_repository.display_all()
    
    def search_airports(self, field_name, value) -> str:
        return self.__airport_repository.search_airports(field_name, value)

    # Aircraft functions


    # Reporting functions


    # Admin functions

    def initialise_database(self):
        db = DBOperations()
        db.initialise_database()