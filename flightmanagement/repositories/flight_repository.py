from datetime import date, time
from flightmanagement.error import RepositoryError
from flightmanagement.models.flight import Flight
from flightmanagement.models.pilot import Pilot
from flightmanagement.repositories.base_repository import BaseRepository

class FlightRepository(BaseRepository):
    """
    Repository responsible for all database operations related to flights.

    This class provides CRUD functionality for Flight domain object,
    encapsulating all SQL access and database interactions. It includes
    methods to retrieve flights by different criteria, and to insert, update,
    and delete flight records. It also provides functionality to support adding
    and removing relief pilots to and from flights.

    The repository maps database rows to domain models and relies on the
    BaseRepository class for connection handling, query execution and exception handling.
    """

    def __init__(self, conn):
        super().__init__(conn)
    
    """
    Core flight operations
    """

    def get_flight_by_id(self, flight_id: int) -> Flight | None:
        """
        Retrieve a single record (with all fields) from the `flights` table
        using the aircraft_id primary key.

        Returns a Flight object constructed from the returned record, 
        or None if no record is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT
                flight_id,
                aircraft_id,
                origin_location_id,
                destination_location_id,
                departure_gate_id,
                arrival_gate_id,
                captain_id,
                first_officer_id,
                flight_number,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            FROM flights
            WHERE flight_id = ?
            """,
            (flight_id, )
        )
        return self.dict_to_flight(row)
    
    def get_flight_summary_by_id(self, flight_id: int) -> dict | None:
        """
        Retrieve a single record (with all fields) from the `vw_flight_summary`
        database view using the aircraft_id primary key.

        `vw_flight_summary` is based on the `flights` table, with one row per
        flight, but with additional denormalised information retrieved from
        related tables. For more information, reference documentation with the
        view create statement in db.py.

        Returns list of dictionaries representing data retrieved from each row
        of the query results. If not records are retrieved, an empty list will be returned.
        """

        row = self._execute_fetchone(
            """
            SELECT
                flight_id,
                flight_number,
                aircraft_registration,
                aircraft_type,
                origin_location,
                origin_town_or_city,
                departure_terminal,
                departure_gate,    
                destination_location,
                destination_town_or_city,
                arrival_terminal,
                arrival_gate,
                captain_name,
                first_officer_name,
                relief_pilots,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            FROM vw_flight_summary
            WHERE flight_id = ?
            """,
            (flight_id, )
        )
        return row

    def search_on_field(self, field_name: str, value) -> list[dict]:
        """
        Retrieve all records (with all fields) from the `vw_flight_summary` denormalised view
        where the specified field contains the specified value.

        This is intended to reduce code duplication by enabling searching against any
        single field in the same method, by injecting the field name into the SQL query.
        Inappropriate SQL injection is guarded against by restricting the allowed values
        for the field_name parameter.

        Returns list of dictionaries representing data retrieved from each row
        of the query results. If not records are retrieved, an empty list will be returned.
        """

        # Limit the values that can be entered as field_name
        # to mitigate SQL injection risk
        allowed_search_fields = {
            "flight_id",
            "flight_number",
            "aircraft_registration",
            "aircraft_type",
            "origin_location",
            "origin_town_or_city",
            "departure_terminal",
            "departure_gate",    
            "destination_location",
            "destination_town_or_city",
            "arrival_terminal",
            "arrival_gate",
            "captain_name",
            "first_officer_name",
            "relief_pilots",
            "scheduled_departure_date",
            "scheduled_departure_time",
            "scheduled_arrival_date",
            "scheduled_arrival_time",
            "confirmed_departure_date",
            "confirmed_departure_time",
            "confirmed_arrival_date",
            "confirmed_arrival_time",
            "flight_status"
        }
        if field_name not in allowed_search_fields:
            raise RepositoryError("Invalid search field")

        sql = f"""
            SELECT
                flight_id,
                flight_number,
                aircraft_registration,
                aircraft_type,
                origin_location,
                origin_town_or_city,
                departure_terminal,
                departure_gate,    
                destination_location,
                destination_town_or_city,
                arrival_terminal,
                arrival_gate,
                captain_name,
                first_officer_name,
                relief_pilots,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            FROM vw_flight_summary
            WHERE {field_name} = ?
            ORDER BY scheduled_departure_date DESC
        """
        rows = self._execute_fetchall(sql, (value, ))
        
        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list

    def get_flight_list(self) -> list[Flight]:
        """
        Retrieve all records (with all fields) from the `flights` table.

        Used to retrieve Flight objects largely for update and delete operations.

        Returns a list of Flight objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                flight_id,
                aircraft_id,
                origin_location_id,
                destination_location_id,
                departure_gate_id,
                arrival_gate_id,
                captain_id,
                first_officer_id,
                flight_number,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            FROM flights
            ORDER BY scheduled_departure_date DESC, scheduled_departure_time DESC
            """
        )
        
        result_list = []
        for row in rows:
            result_list.append(self.dict_to_flight(row))

        return result_list

    def get_flight_summary_list(self) -> list[dict]:
        """
        Retrieve all records (with all fields) from the `vw_flight_summary` view.

        Used to retrieve more informative and human-readable flight information to display
        to users.

        Returns a list of dictionaries constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                flight_id,
                flight_number,
                aircraft_registration,
                aircraft_type,
                origin_location,
                origin_town_or_city,
                departure_terminal,
                departure_gate,    
                destination_location,
                destination_town_or_city,
                arrival_terminal,
                arrival_gate,
                captain_name,
                first_officer_name,
                relief_pilots,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            FROM vw_flight_summary
            ORDER BY scheduled_departure_date DESC
            """
        )

        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list

    def insert_flight(self, flight: Flight) -> int:
        """
        Inserts a new record into the `flights` table.

        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement flight_id primary key minted by the database
        for the new record.
        """

        row = self._execute_fetchone(
            """
            INSERT INTO flights (                
                aircraft_id,
                origin_location_id,
                destination_location_id,
                departure_gate_id,
                arrival_gate_id,
                captain_id,
                first_officer_id,
                flight_number,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            )
            VALUES (
                :aircraft_id,
                :origin_location_id,
                :destination_location_id,
                :departure_gate_id,
                :arrival_gate_id,
                :captain_id,
                :first_officer_id,
                :flight_number,
                :scheduled_departure_date,
                :scheduled_departure_time,
                :scheduled_arrival_date,
                :scheduled_arrival_time,
                :confirmed_departure_date,
                :confirmed_departure_time,
                :confirmed_arrival_date,
                :confirmed_arrival_time,
                :flight_status
            )
            RETURNING flight_id
            """,
            {
                "aircraft_id": flight.aircraft_id,
                "origin_location_id": flight.origin_location_id, 
                "destination_location_id": flight.destination_location_id,
                "departure_gate_id": flight.departure_gate_id,
                "arrival_gate_id": flight.arrival_gate_id,
                "captain_id": flight.captain_id,
                "first_officer_id": flight.first_officer_id,
                "flight_number": flight.flight_number,
                "scheduled_departure_date": flight.scheduled_departure_date.strftime("%Y-%m-%d"),
                "scheduled_departure_time": flight.scheduled_departure_time.strftime("%H:%M"),
                "scheduled_arrival_date": flight.scheduled_arrival_date.strftime("%Y-%m-%d"),
                "scheduled_arrival_time": flight.scheduled_arrival_time.strftime("%H:%M"),
                "confirmed_departure_date": flight.confirmed_departure_date.strftime("%Y-%m-%d") if flight.confirmed_departure_date else None,
                "confirmed_departure_time": flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None,
                "confirmed_arrival_date": flight.confirmed_arrival_date.strftime("%Y-%m-%d") if flight.confirmed_arrival_date else None,
                "confirmed_arrival_time": flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None,
                "flight_status": flight.flight_status
            }
        )

        if row is None:
            raise RepositoryError("Flight insert failed")

        return row["flight_id"]

    def update_flight(self, flight: Flight):
        """
        Updates all fields in the selected record in the `flights` table.

        Field values are derived from the attributes of the Flight object.
        Unpopulated parameters will have default values assigned according to
        the database schema.

        The query updates all fields in the record, even if the new values are
        identical to the existing values in the database record. This is intended
        to simplify the database update code, but might need revisiting in the
        future if detailed data provenance and audit functionality requirements emerge.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            UPDATE flights
            SET
                aircraft_id = ?,
                origin_location_id = ?,
                destination_location_id = ?,
                departure_gate_id = ?,
                arrival_gate_id = ?,
                captain_id = ?,
                first_officer_id = ?,
                flight_number = ?,
                scheduled_departure_date = ?,
                scheduled_departure_time = ?,
                scheduled_arrival_date = ?,
                scheduled_arrival_time = ?,
                confirmed_departure_date = ?,
                confirmed_departure_time = ?,
                confirmed_arrival_date = ?,
                confirmed_arrival_time = ?,
                flight_status = ?
            WHERE flight_id = ?
            """,
            (                
                flight.aircraft_id,
                flight.origin_location_id,
                flight.destination_location_id,
                flight.departure_gate_id,
                flight.arrival_gate_id,
                flight.captain_id,
                flight.first_officer_id,
                flight.flight_number,
                flight.scheduled_departure_date.strftime("%Y-%m-%d") if flight.scheduled_departure_date else None,
                flight.scheduled_departure_time.strftime("%H:%M") if flight.scheduled_departure_time else None,
                flight.scheduled_arrival_date.strftime("%Y-%m-%d") if flight.scheduled_arrival_date else None,
                flight.scheduled_arrival_time.strftime("%H:%M") if flight.scheduled_arrival_time else None,
                flight.confirmed_departure_date.strftime("%Y-%m-%d") if flight.confirmed_departure_date else None,
                flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None,
                flight.confirmed_arrival_date.strftime("%Y-%m-%d") if flight.confirmed_arrival_date else None,
                flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None,
                flight.flight_status,
                flight.flight_id
            )
        )

    def delete_flight(self, flight: Flight):
        """
        Delete a single record from the `flights` table identified by
        the flight_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM flights
            WHERE flight_id = ?
            """,
            (flight.flight_id, )
        )

    def dict_to_flight(self, data: dict | None) -> Flight | None:
        """
        Create and populate the attributes of a Flight object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Flight domain model, and violations raised as domain model
        exceptions.

        Returns the Flight object, or None if the dictionary is missing or
        empty. 
        """

        if data is None or len(data) == 0:
            return None

        return Flight(
            flight_id = data["flight_id"],
            aircraft_id = data["aircraft_id"],
            origin_location_id = data["origin_location_id"], 
            destination_location_id = data["destination_location_id"],
            departure_gate_id = data["departure_gate_id"],
            arrival_gate_id = data["arrival_gate_id"],
            captain_id = data["captain_id"],
            first_officer_id = data["first_officer_id"],
            flight_number = data["flight_number"],
            scheduled_departure_date = date.fromisoformat(data["scheduled_departure_date"]),
            scheduled_departure_time = time.fromisoformat(data["scheduled_departure_time"]),
            scheduled_arrival_date = date.fromisoformat(data["scheduled_arrival_date"]),
            scheduled_arrival_time = time.fromisoformat(data["scheduled_arrival_time"]),
            confirmed_departure_date = date.fromisoformat(data["confirmed_departure_date"]) if data["confirmed_departure_date"] else None,
            confirmed_departure_time = time.fromisoformat(data["confirmed_departure_time"]) if data["confirmed_departure_time"] else None,
            confirmed_arrival_date = date.fromisoformat(data["confirmed_arrival_date"]) if data["confirmed_arrival_date"] else None,
            confirmed_arrival_time = time.fromisoformat(data["confirmed_arrival_time"]) if data["confirmed_arrival_time"] else None,
            flight_status = data["flight_status"]
        )
    
    """
    Relief pilot handling
    """

    def get_relief_pilots_by_flight_id(self, flight_id: int) -> list[int]:
        """
        Retrieve a list of the unique IDs of all staff members linked as relief pilots to the specified
        flight.

        Returns a list of staff_member_ids as integers.

        """

        rows = self._execute_fetchall(
            """
            SELECT staff_member_id
            FROM flight_relief_pilots
            WHERE flight_id = ?
            """,
            (flight_id, )
        )

        result_list = []
        for row in rows:
            result_list.append(row["staff_member_id"])

        return result_list

    def insert_relief_pilot(self, flight: Flight, staff_member_id: int):
        """
        Inserts a new record into the `flight_relief_pilots` table.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            INSERT INTO flight_relief_pilots (
                flight_id,
                staff_member_id
            )
            VALUES (
                :flight_id,
                :staff_member_id
            )
            """,
            {
                "flight_id": flight.flight_id,
                "staff_member_id": staff_member_id
            }
        )

    def delete_relief_pilot(self, flight: Flight, staff_member_id: int):
        """
        Delete a single record from the `flight_relief_pilots` table identified by
        the flight_id / staff_member_id composite primary key.

        """

        self._execute(
            """
            DELETE FROM flight_relief_pilots
            WHERE flight_id = ?
            AND staff_member_id = ?
            """,
            (flight.flight_id, staff_member_id)
        )