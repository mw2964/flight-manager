from flightmanagement.repositories.airport_repository import AirportRepository

class AirportService:

    def __init__(self):
        self.__airport_repository = AirportRepository()

    # Airport functions

    def add_airport(self, code: str, name: str, city: str, country: str, region: str):
        self.__airport_repository.add_airport(code, name, city, country, region)

    def update_airport(self, id: int, code: str, name: str, city: str, country: str, region: str):
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
    
    def search_airports(self, field_name: str, value) -> str:
        return self.__airport_repository.search_airports(field_name, value)