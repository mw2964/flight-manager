from prettytable import PrettyTable
from flightmanagement.models.airport import Airport
from flightmanagement.db.db import DBOperations

class AirportRepository:

    def __init__(self):
        self.__db = DBOperations()

    def get_airport_by_id(self, id: int) -> Airport | None:
        
        result = self.__db.get_row_by_id("airport", id)
        
        if result:
            airport = Airport(
                id = result[0],
                code = result[1],
                name = result[2],
                city = result[3],
                country = result[4],
                region = result[5]
            )
            return airport

    def get_airport_by_code(self, code: str) -> Airport | None:

        id = self.__db.search_data("airport", "code", code)
        
        if id:
            return self.get_airport_by_id(id)

    def get_airport_list(self) -> list[Airport] | None:
        data = self.__db.select_all("airport")

        if not data:
            return None
        
        airport = []
        for row in data:
            airport.append(Airport(row[0], row[1], row[2], row[3], row[4], row[5]))

        return airport

    def add_airport(self, code: str, name: str, city: str, country: str, region: str) -> bool:        
        
        try:
            # Add the new airport to the database
            data = {
                "code": code, 
                "name": name,
                "city": city, 
                "country": country,
                "region": region
            }
            self.__db.insert_row("airport", data)

            return True
        except Exception as e:
            print(e)
            return False

    def update_airport(self, id: int, updates: dict):
        self.__db.update_row("airport", id, updates)
    
    def delete_airport(self, id: int):
        self.__db.delete_row("airport", id)
    
    def search_airports(self, field_name: str, value) -> str:
        result_id = self.__db.search_data("airport", field_name, value)
        
        if result_id:
            airport = self.get_airport_by_id(result_id)
            if airport:
                return "\nMatch found:\n" + self.display_record(airport)
            else:
                return "\nNo matching records"
        else:
            return "\nNo matching records"

    def display_all(self) -> str:
        
        data = self.__db.select_all("airport")

        table = PrettyTable(["Airport ID", "Code", "Name", "City", "Country", "Region"])
        table.align = "l"

        if data:
            for row in data:
                table.add_row(row)
    
        return str(table)
    
    def display_record(self, airport: Airport) -> str:
        record_string = f"""
> Airport ID: {airport.id}
> Code: {airport.code}
> Name: {airport.name}
> City: {airport.city}
> Country: {airport.country}
> Region: {airport.region}
        """
        return record_string
    