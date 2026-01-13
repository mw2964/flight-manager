from datetime import datetime
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.repositories.airport_repository import AirportRepository
from flightmanagement.repositories.flight_repository import FlightRepository

class FlightService:

    def __init__(self):
        self.__flight_repository = FlightRepository()
        self.__aircraft_repository = AircraftRepository()
        self.__airport_repository = AirportRepository()
    
    def get_flight_list(self) -> str:
        return self.__flight_repository.get_flights_view()
    
    def delete_flight(self, id: int):
        self.__flight_repository.delete_flight(id)

    def add_flight(self, flight_number: str, aircraft_id: int, origin_id: int, destination_id: int, pilot_id: int, copilot_id: int, departure_date: str, departure_time: str, arrival_date: str, arrival_time: str):
        self.__flight_repository.add_flight(flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_date, departure_time, arrival_date, arrival_time)

    def update_flight(self, id: int, flight_number: str, aircraft_id: int, origin_id: int, destination_id: int, pilot_id: int, copilot_id: int, departure_date_scheduled: str | None, departure_time_scheduled: str | None, arrival_date_scheduled: str | None, arrival_time_scheduled: str | None, departure_date_actual: str | None, departure_time_actual: str | None, arrival_date_actual: str | None, arrival_time_actual: str | None, status: str):
        
        flight = self.__flight_repository.get_flight_by_id(id)
        
        if flight:
            updates = {}
            if flight_number != flight.flight_number:
                updates["flight_number"] = flight_number
            if aircraft_id != flight.aircraft_id:
                updates["aircraft_id"] = aircraft_id
            if origin_id != flight.origin_id:
                updates["origin_id"] = origin_id
            if destination_id != flight.destination_id:
                updates["destination_id"] = destination_id
            if pilot_id != flight.pilot_id:
                updates["pilot_id"] = pilot_id
            if copilot_id != flight.copilot_id:
                updates["copilot_id"] = copilot_id
            if datetime.strptime(f"{departure_date_scheduled} {departure_time_scheduled}", "%Y-%m-%d %H:%M") != flight.departure_time_scheduled:
                updates["departure_time_scheduled"] = f"{departure_date_scheduled} {departure_time_scheduled}"
            if datetime.strptime(f"{arrival_date_scheduled} {arrival_time_scheduled}", "%Y-%m-%d %H:%M") != flight.arrival_time_scheduled:
                updates["arrival_time_scheduled"] = f"{arrival_date_scheduled} {arrival_time_scheduled}", "%Y-%m-%d %H:%M"
            if datetime.strptime(f"{departure_date_actual} {departure_time_actual}", "%Y-%m-%d %H:%M") != flight.departure_time_actual:
                updates["departure_time_actual"] = f"{departure_date_actual} {departure_time_actual}", "%Y-%m-%d %H:%M"
            if datetime.strptime(f"{arrival_date_actual} {arrival_time_actual}", "%Y-%m-%d %H:%M") != flight.arrival_time_actual:
                updates["arrival_time_actual"] = f"{arrival_date_actual} {arrival_time_actual}", "%Y-%m-%d %H:%M"
            if status != flight.status:
                updates["status"] = status

            self.__flight_repository.update_flight(id, updates)

    def get_flight(self, id: int):
        return self.__flight_repository.get_flight_by_id(id)

    def get_aircraft(self, aircraft_registration: str) -> int | None:
        aircraft = self.__aircraft_repository.get_aircraft_by_registration(aircraft_registration)        
        if aircraft:
            return aircraft.id
        
    def get_airport(self, airport_code: str) -> int | None:
        airport = self.__airport_repository.get_airport_by_code(airport_code)        
        if airport:
            return airport.id
    
    def get_flight_choices(self, flight_number: str = "") -> list:
        flights = self.__flight_repository.get_flight_list()
        
        flight_choices = []

        if flights:
            for flight in flights:
                if flight_number == "" or flight[1] == flight_number:
                    flight_choices.append((flight[0], f"{flight[1]} ({flight[2]} to {flight[3]}, departure: {flight[4]}, status: {flight[5]})"))

        return flight_choices