from datetime import datetime
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.repositories.airport_repository import AirportRepository
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.repositories.flight_repository import FlightRepository
from flightmanagement.db.db import DBOperations

class FlightService:

    def __init__(self):
        self.__flight_repository = FlightRepository()
        self.__aircraft_repository = AircraftRepository()
    
    # Flight functions

    def get_flight_list(self) -> str:
        return self.__flight_repository.get_flights_view()
        #return self.__flight_repository.display_all()
    
    def delete_flight(self, id: int):
        self.__flight_repository.delete_flight(id)

    def add_flight(self, flight_number: str, aircraft: str, origin: str, destination: str, pilot_id: int, copilot_id: int, departure_date: str, departure_time: str, arrival_date: str, arrival_time: str):

        aircraft_id = self.__aircraft_repository.search_aircraft("registration", aircraft)[0]
        print(aircraft_id)


    # Reporting functions


    # Admin functions

