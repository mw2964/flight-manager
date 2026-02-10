from datetime import datetime, timedelta
import pandas as pd
from pandas import DataFrame
from prettytable import PrettyTable
from flightmanagement.error import MissingData, DependentRecords, DuplicateRecord, InvalidData, ForeignKeyDependencyViolation, ForeignKeyInvalidViolation, UniqueConstraintViolation, CheckConstraintViolation, MissingNotNullViolation
from flightmanagement.services.service_utils import format_table
from flightmanagement.repositories.aircraft_repository import AircraftRepository
from flightmanagement.repositories.location_repository import LocationRepository
from flightmanagement.repositories.flight_repository import FlightRepository
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.flight import Flight
from flightmanagement.db.db import transaction

class FlightService:

    def __init__(self, conn, flight_repository = None):
        self.conn = conn
        self.__flight_repository = (
            flight_repository or FlightRepository(self.conn)
        )
        self.__aircraft_repository = AircraftRepository(self.conn)
        self.__location_repository = LocationRepository(self.conn)
        self.__pilot_repository = PilotRepository(self.conn)

    # Edit and delete

    def add_flight(self, flight: Flight) -> int:
        try:
            with transaction(self.conn):
                return self.__flight_repository.insert_flight(flight)
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def update_flight(self,flight: Flight):
        try:
            with transaction(self.conn):
                self.__flight_repository.update_flight(flight)
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def delete_flight(self, flight: Flight):
        if flight.flight_id is None:
            raise ValueError("Flight to delete lacks an ID")
        
        try:
            with transaction(self.conn):
                self.__flight_repository.delete_flight(flight)
        except ForeignKeyDependencyViolation as e:
            raise DependentRecords(e)

    def assign_pilot_to_flight(self, flight: Flight):
        with transaction(self.conn):
            self.__flight_repository.update_flight(flight)

    def add_relief_pilot(self, flight: Flight, staff_member_id: int):
        with transaction(self.conn):
            self.__flight_repository.insert_relief_pilot(flight, staff_member_id)

    def remove_relief_pilot(self, flight: Flight, staff_member_id: int):
        with transaction(self.conn):
            self.__flight_repository.delete_relief_pilot(flight, staff_member_id)

    # Retrieve flight information

    def get_flight_table(self) -> str:
        data = self.__flight_repository.get_flight_summary_list()

        if data is None:
            return ""
        
        df = pd.json_normalize(data)
        
        return self.get_results_view(df)

    def get_flight_by_id(self, id: int) -> Flight | None:
        return self.__flight_repository.get_flight_by_id(id)
    
    def get_flight_summary_by_id(self, id: int) -> dict | None:
        return self.__flight_repository.get_flight_summary_by_id(id)
    
    def search_flights(self, field_name: str, value) -> list[dict]:
        return self.__flight_repository.search_on_field(field_name, value)

    def get_flights_full_text(self, search_text: str | None) -> DataFrame:
        data = self.__flight_repository.get_flight_summary_list()
        df = pd.json_normalize(data)

        if search_text is not None:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)

            # Filtered dataframe
            filtered_df = df[mask]
            return(filtered_df)
        else:
            return(df)

    def get_flight_choices(self, flight_number: str = "", id_list: list | None = None) -> list:
        flights = self.__flight_repository.get_flight_summary_list()
        
        flight_choices = []

        if flights:
            for flight in flights:
                if id_list is not None and flight["flight_id"] not in id_list:
                    continue
                if flight_number == "" or flight["flight_number"] == flight_number:                    
                    flight_choices.append((flight["flight_id"], self.get_flight_summary(flight)))

        return flight_choices
    
    def get_results_view(self, df) -> str:
                
        # Initialise the table
        table = PrettyTable([
            "ID",
            "Flight no.",
            "Aircraft",
            "From",
            "To",
            "Pilots",
            "Dept. (scheduled)",
            "Arr. (scheduled)",
            "Status"
            ],
        )        
        
        # Populate table rows
        for i, row in df.iterrows():

            # Format and combine some fields for readability and to reduce table width
            origin = f"{row['origin_location']}\n({row['origin_town_or_city']})"
            destination = f"{row['destination_location']}\n({row['destination_town_or_city']})"

            pilots = ""
            if row['captain_name'] != "":
                pilots += f"{row['captain_name']} (c)"
            if row['first_officer_name'] != "":
                if len(pilots) > 0:
                    pilots += "\n"
                pilots += f"{row['first_officer_name']} (fo)"
            if row['relief_pilots'] != "":
                if len(pilots) > 0:
                    pilots += "\n"
                pilots += f"{row['relief_pilots'].replace(", ", "\n")}"

            departure_date_formatted = datetime.strptime(row['scheduled_departure_date'],"%Y-%m-%d").strftime("%d/%m/%Y")
            arrival_date_formatted = datetime.strptime(row['scheduled_arrival_date'],"%Y-%m-%d").strftime("%d/%m/%Y")
            departure = f"{departure_date_formatted}\n{row['scheduled_departure_time']}"
            arrival = f"{arrival_date_formatted}\n{row['scheduled_arrival_time']}"

            table.add_row([
                row["flight_id"],
                row["flight_number"],
                row["aircraft_registration"],
                origin,
                destination,
                pilots,
                departure,
                arrival,
                row['flight_status']
            ])
        return format_table(table)
    
    def get_flight_summary(self, flight: dict) -> str:        
        departure = f"{datetime.strptime(flight["scheduled_departure_date"], '%Y-%m-%d').strftime("%d/%m/%Y")} {flight["scheduled_departure_time"]}"
        spaces = 10 - len(flight["flight_number"])
        id_spaces = 3 - len(str(flight["flight_id"]))
        return f"Flight ID {flight["flight_id"]}{' ' * id_spaces} -> {flight["flight_number"]}{' ' * spaces}{flight["origin_location"]} to {flight["destination_location"]} | Departure: {departure} | Status: {flight["flight_status"]}"

    # Retrieve related information

    def get_flight_relief_pilots(self, flight: Flight) -> list:
        if flight.flight_id is None:
            raise ValueError("Missing flight ID")
        return self.__flight_repository.get_relief_pilots_by_flight_id(flight.flight_id)

    def get_flight_relief_pilot_choices(self, flight: Flight) -> list:
        id_list = self.get_flight_relief_pilots(flight)

        relief_pilots = []
        if id_list:
            for id in id_list:
                pilot = self.__pilot_repository.get_pilot_by_id(id)
                relief_pilots.append((id, str(pilot)))

        return relief_pilots

    def get_available_pilot_choices(self, departure_time: datetime, arrival_time: datetime, already_on_flight: list = [], flight_id: int | None = None) -> list:
        
        # Get pilots who are on leave on the flight date
        on_leave_ids = self.__pilot_repository.get_staff_on_leave_by_date_range(departure_time.date(), arrival_time.date())

        # Get pilots who are on overlapping flights
        overlapping_ids = self.__pilot_repository.get_staff_on_flights_by_date_range(departure_time, arrival_time, flight_id)

        # Combine the two lists (removing duplicates)
        unavailable_pilot_ids = list(set(on_leave_ids) | set(overlapping_ids))

        all_pilots = self.__pilot_repository.get_pilot_list()

        available_pilot_choices = []
        if all_pilots:
            for pilot in all_pilots:

                # Skip pilots already assigned to the flight or in the unavailable list
                if pilot.staff_member_id in already_on_flight or pilot.staff_member_id in unavailable_pilot_ids:
                    continue

                # Skip pilots who have already exceeded their 28-day rolling flight time limit at the time of departure
                # (according to hours already logged)
                from_date = departure_time.date() - timedelta(days=28)
                if self.__pilot_repository.get_pilot_flight_hours_for_period(pilot.staff_member_id, from_date, departure_time.date()) >= 100:
                    continue
                
                available_pilot_choices.append((pilot.staff_member_id, str(pilot)))

        return available_pilot_choices