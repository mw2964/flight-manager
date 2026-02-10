from flightmanagement.error import RepositoryError
from flightmanagement.repositories.base_repository import BaseRepository
from flightmanagement.models.pilot import Pilot
from datetime import date, datetime

class PilotRepository(BaseRepository):
    """
    Repository responsible for all database operations related to pilots.

    This class provides CRUD functionality for Pilot domain object,
    encapsulating all SQL access and database interactions. It includes
    methods to retrieve pilots by different criteria, and to insert, update,
    and delete pilot records. It also provides functionality to support calculating
    pilot availability for flight scheduling, and for pilot flight hours logging and
    leave bookings.

    The repository maps database rows to domain models and relies on the
    BaseRepository class for connection handling, query execution and exception handling.
    """

    def __init__(self, conn):
        super().__init__(conn)

    """
    Core pilot functionality
    """

    def get_pilot_by_id(self, staff_member_id: int) -> Pilot | None:
        """
        Retrieve a single record (with all fields) from the `vw_staff_pilots`
        database view (a combined view of the `pilots` and `staff_members` tables),
        using the staff_member_id primary key shared by those two tables.

        Returns a Pilot object constructed from the returned record, 
        or None if no record is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT 
                staff_member_id,
                employee_number,
                first_name,
                family_name,
                employment_status,
                employment_start_date,
                employment_end_date,
                license_number,
                license_type,
                license_expiration_date
            FROM vw_staff_pilots
            WHERE staff_member_id = ?
            """,
            (staff_member_id, )
        )     
        return self.dict_to_pilot(row)

    def get_pilot_list(self) -> list:
        """
        Retrieve all records (with all fields) from the `vw_staff_pilots` view.

        Returns a list of Pilot objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT 
                staff_member_id,
                employee_number,
                first_name,
                family_name,
                employment_status,
                employment_start_date,
                employment_end_date,
                license_number,
                license_type,
                license_expiration_date
            FROM vw_staff_pilots
            ORDER BY family_name, first_name
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_pilot(row))

        return result_list

    def search_on_field(self, field_name: str, value) -> list:
        """
        Retrieve all records (with all fields) from the `vw_staff_pilots` database
        view where the provided field name has the provided value.

        This is intended to reduce code duplication by enabling searching against any
        single field in the same method, by injecting the field name into the SQL query.
        Inappropriate SQL injection is guarded against by restricting the allowed values
        for the field_name parameter.

        Returns a list of Pilot objects constructed from the returned records.
        """

        # Limit the values that can be entered as field_name
        # to mitigate SQL injection risk
        allowed_search_fields = {
            "staff_member_id",
            "employee_number",
            "first_name",
            "family_name",
            "employment_status",
            "employment_start_date",
            "employment_end_date",
            "license_number",
            "license_type",
            "license_expiration_date"
        }
        if field_name not in allowed_search_fields:
            raise RepositoryError("Invalid search field")

        sql = f"""
            SELECT 
                staff_member_id,
                employee_number,
                first_name,
                family_name,
                employment_status,
                employment_start_date,
                employment_end_date,
                license_number,
                license_type,
                license_expiration_date
            FROM vw_staff_pilots
            WHERE {field_name} = ?
            ORDER BY family_name, first_name
        """
        rows = self._execute_fetchall(sql, (value, ))
        
        result_list = []
        for row in rows:
            result_list.append(self.dict_to_pilot(row))

        return result_list

    def insert_pilot(self, pilot: Pilot) -> int:
        """
        Inserts a new record into each of the `staff_members` and `pilots` tables.

        The `staff_members` insert must happen first, as this mints the new staff_member_id
        identifier used as the primary key by both tables.
        
        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement staff_member_id primary key minted by the database
        for the new record.
        """

        # Insert the `staff_members` record first
        row = self._execute_fetchone(
            """
            INSERT INTO staff_members
                (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                (:employee_number, :first_name, :family_name, :employment_status, :employment_start_date, :employment_end_date)
            RETURNING staff_member_id
            """,
            {
                "employee_number": pilot.employee_number,
                "first_name": pilot.first_name, 
                "family_name": pilot.family_name,
                "employment_status": pilot.employment_status,
                "employment_start_date": pilot.employment_start_date.strftime("%Y-%m-%d"),
                "employment_end_date": pilot.employment_end_date.strftime("%Y-%m-%d") if pilot.employment_end_date else None
            }
        )
        if row is None:
            raise RepositoryError("Failed to insert staff member.")

        # Retrieve the new staff_member_id primary key generated by the database,
        # as it's required to insert as the primary key in the new `pilots` record.
        new_id = row["staff_member_id"]

        # Insert the `pilots` record
        self._execute(
            """
            INSERT INTO pilots
                (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (:staff_member_id, :license_number, :license_type, :license_expiration_date)
            """,
            {
                "staff_member_id": row["staff_member_id"],
                "license_number": pilot.license_number,
                "license_type": pilot.license_type,
                "license_expiration_date": pilot.license_expiration_date.strftime("%Y-%m-%d") if pilot.license_expiration_date else None
            }
        )
        if row is None:
            raise RepositoryError("Failed to insert pilot.")
        
        return row["staff_member_id"]

    def update_pilot(self, pilot: Pilot) -> None:
        """
        Updates all fields in the selected records in the `staff_members`
        and `pilots` tables.

        Both tables are affected, as the Pilot model represents a composite of
        data from both tables (representing a one-to-one cardinality between the
        two).

        Field values are derived from the attributes of the Pilot object.
        Unpopulated parameters will have default values assigned according to
        the database schema.

        The query updates all fields in the records, even if the new values are
        identical to the existing values in those database records. This is intended
        to simplify the database update code, but might need revisiting in the
        future if detailed data provenance and audit functionality requirements emerge.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        # Update the `staff_members` record
        self._execute(
            """
            UPDATE staff_members
            SET
                employee_number = ?,
                first_name = ?,
                family_name = ?,
                employment_status = ?,
                employment_start_date = ?,
                employment_end_date = ?
            WHERE staff_member_id = ?
            """,
            (
                pilot.employee_number,
                pilot.first_name,
                pilot.family_name,
                pilot.employment_status,
                pilot.employment_start_date.strftime("%Y-%m-%d"),
                pilot.employment_end_date.strftime("%Y-%m-%d") if pilot.employment_end_date else None,
                pilot.staff_member_id
            )
        )
        
         # Update the `pilots` record
        self._execute(
            """
            UPDATE pilots
            SET
                license_number = ?,
                license_type = ?,
                license_expiration_date = ?
            WHERE staff_member_id = ?
            """,
            (
                pilot.license_number,
                pilot.license_type,
                pilot.license_expiration_date.strftime("%Y-%m-%d") if pilot.license_expiration_date else None,
                pilot.staff_member_id
            )
        )

    def delete_pilot(self, pilot: Pilot) -> None:
        """
        Delete a single record from the `pilots` table identified by
        the staff_member_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM pilots
            WHERE staff_member_id = ?
            """,
            (pilot.staff_member_id, )
        )

    def delete_staff_member(self, pilot: Pilot) -> None:
        """
        Delete a single record from the `pilots` table identified by
        the staff_member_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        If a related record still exists in the `pilots` table, this will
        raise a DependentRecords repository exception.
        """

        self._execute(
            """
            DELETE FROM staff_members
            WHERE staff_member_id = ?
            """,
            (pilot.staff_member_id, )
        )
    
    """
    Pilot scheduling and availability
    """

    def get_pilot_schedule_by_id(self, staff_member_id: int) -> list:
        """
        Retrieve a summary of all flights where the input pilot is either
        captain, first officer or one of the relief pilots.

        This query constructs a normalised view of flight_id and pilot role
        from the union of three subqueries:

            1. flights where the pilot is captain (providing pilot_role of 'captain')
            2. flights where the pilot is first officer (providing pilot_role of 'first officer')
            3. flights where the pilot is a relief pilot (providing pilot_role of 'relief pilot')
        
        Each of these are filtered to records related to the pilot in question. The view is then
        joined with the main flights summary view in order to retrieve additional information
        about each of those flights.

        Although it's possible for the query to return more than one row for a single flight,
        this should be prevented by flight model domain validation which prevents users from
        selecting the same pilot as both captain and first officer. The primary key constraint
        on the flight_id and staff_member_id fields of the flight_relief_pilots table prevents
        any single pilot from being added to a flight as a relief pilot more than once.

        Returns a list of dictionaries representing the data rows returned from the query.

        """

        rows = self._execute_fetchall(
            """
            SELECT
                a.flight_id,
                a.pilot_role,
                f.flight_number,
                f.origin_location,
                f.destination_location,
                f.scheduled_departure_date,
                f.scheduled_departure_time,
                f.scheduled_arrival_date,
                f.scheduled_arrival_time,
                f.flight_status
            FROM
                (SELECT
                    flight_id,
                    'captain' as pilot_role
                FROM flights
                WHERE captain_id = ?
                UNION
                SELECT
                    flight_id,
                    'first officer' as pilot_role
                FROM flights
                WHERE first_officer_id = ?
                UNION
                SELECT
                    DISTINCT flight_id,
                    'relief pilot' as pilot_role
                FROM flight_relief_pilots
                WHERE staff_member_id = ?
            ) a
            INNER JOIN vw_flight_summary f ON f.flight_id = a.flight_id
            ORDER BY f.scheduled_arrival_date, f.scheduled_arrival_time
            """,
            (staff_member_id, staff_member_id, staff_member_id)
        )

        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list

    def get_staff_on_leave_by_date_range(self, date_from: date, date_to: date) -> list[int]:
        """
        Retrieve a list of the unique IDs of all staff members with a leave booking between
        the start date and leave date inclusive.

        Returns a list of dictionaries representing the data rows returned from the query.

        """

        rows = self._execute_fetchall(
            """
            SELECT staff_member_id
            FROM leave_bookings
            WHERE leave_date >= ?
            AND leave_date <= ?
            """,
            (date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d"))
        )

        result_list = []
        for row in rows:
            result_list.append(row["staff_member_id"])

        return result_list
    
    def get_staff_on_flights_by_date_range(self, date_from: datetime, date_to: datetime, exclude_flight_id: int | None = None) -> list[int]:
        """
        Retrieve a list of the unique IDs of all staff members that play any pilot role on a
        flight scheduled between the start date and leave date inclusive.

        This method applies two queries:
        
            1. Retrieves the captain_id and first_officer_id of all flights in the `flights` table
               where the range from scheduled departure date/time to scheduled arrival data/time
               overlaps at any point with the date_from to date_to range passed into the method.

            2. Retrieves the staff_member_id from all records in the `flight_relief_pilots` table
               that are linked (through flight_id foreign key) to records in the `flights` table
               which fulfil the same criteria as described in 1 above.

        Dates and times are converted to datetimes for comparison purposes by concatenating those
        atomised fields. Although SQLite does not have a formal datetime data type, it does facilitate
        logical operations between text fields formatted as ISO dates and times that provide the expected results.

        For both of those queries, an additional and optional clause may be applied to include a specific flight_id
        in the query filter. In pilot availability checking, this is used to ensure that pilots are not reported
        as being unavailable for a flight that they are already assigned to and therefore excluded from UI
        picklists when editing that flight's information.

        All three of these ID fields are foreign keys referencing the staff_member_id primary key
        of the `pilots` and `staff_members` tables. The method then returns a combined and
        de-duplicated list of those staff_member_ids.

        Returns a list of staff_member_ids as integers.

        """
        
        params: list = [date_to, date_from]
        if exclude_flight_id is not None:
            sql_extra_clause = "AND flight_id <> ?"
            params.append(exclude_flight_id)
        else:
            sql_extra_clause = ""
        
        sql = f"""
            SELECT captain_id, first_officer_id
            FROM flights
            WHERE datetime(scheduled_departure_date || ' ' || scheduled_departure_time) <= ?
            AND datetime(scheduled_arrival_date || ' ' || scheduled_arrival_time) >= ?
            {sql_extra_clause}
            """
        rows = self._execute_fetchall(sql, tuple(params))

        result_list = []
        for row in rows:
            if row["captain_id"] and row["captain_id"] not in result_list:
                result_list.append(row["captain_id"])
            if row["first_officer_id"] and row["first_officer_id"] not in result_list:
                result_list.append(row["first_officer_id"])

        sql = f"""
            SELECT staff_member_id
            FROM flight_relief_pilots
            WHERE flight_id IN (
                SELECT flight_id
                FROM flights
                WHERE datetime(scheduled_departure_date || ' ' || scheduled_departure_time) <= ?
                AND datetime(scheduled_arrival_date || ' ' || scheduled_arrival_time) >= ?
                {sql_extra_clause}
            )
            """
        rows = self._execute_fetchall(sql, tuple(params))

        for row in rows:
            if row["staff_member_id"] and row["staff_member_id"] not in result_list:
                result_list.append(row["staff_member_id"])

        return result_list

    def get_pilot_flight_hours_for_period(self, staff_member_id: int, start_date: date, end_date: date) -> float:
        """
        Retrieve the total flight hours logged by a defined pilot over a defined date range.

        This query sums the flight hours in the `flight_time_logs` table for records matching
        the staff_member_id and where the effective date is between the start_date and end_date
        parameters (inclusive). The coalesce function is used to return 0.0 rather than NULL
        if no records match the filter, so that the output is always a valid float.

        As an aggregation query, this should always return one row in the results. If this
        is not the case, an exception is raised.

        Returns total hours as a float.

        """

        row = self._execute_fetchone(
            """
            SELECT
                coalesce(SUM(flight_hours), 0.0) AS total_hours
            FROM flight_time_logs
            WHERE staff_member_id = ?
            AND effective_date >= ?
            AND effective_date <= ?
            """,
            (staff_member_id, start_date, end_date)
        )
        if row is None:
            raise RepositoryError("Failed to retrieve pilot flight hours.")
        return float(row["total_hours"])


    def dict_to_pilot(self, data: dict | None) -> Pilot | None:
        """
        Create and populate the attributes of an Pilot object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Pilot domain model, and violations raised as domain model
        exceptions.

        Returns the Pilot object, or None if the dictionary is missing or
        empty. 
        """

        if data is None or len(data) == 0:
            return None

        return Pilot(
            staff_member_id = data["staff_member_id"],
            employee_number = data["employee_number"],
            first_name = data["first_name"],
            family_name = data["family_name"],
            employment_start_date = date.fromisoformat(data["employment_start_date"]),
            employment_status = data["employment_status"],
            employment_end_date = date.fromisoformat(data["employment_end_date"]) if data["employment_end_date"] is not None else None,
            license_number = data["license_number"],
            license_type = data["license_type"],
            license_expiration_date = date.fromisoformat(data["license_expiration_date"]) if data["license_expiration_date"] is not None else None
        )
    
    """
    Leave booking functionality
    """
    
    def get_leave_bookings_by_staff_member_id(self, staff_member_id: int) -> list[dict]:
        """
        Retrieve all records (with all fields) from the `leave_bookings` table
        for the defined staff member.

        Returns a list of dictionaries containing the data of each row returned.
        """

        rows = self._execute_fetchall(
            """
            SELECT 
                staff_member_id,
                leave_date,
                leave_type
            FROM leave_bookings
            WHERE staff_member_id = ?
            """,
            (staff_member_id, )
        )
        return rows

    def get_leave_record_by_staff_member_id_and_date(self, staff_member_id: int, leave_date: date) -> dict | None:
        """
        Retrieve a record (with all fields) from the `leave_bookings` table
        for the defined staff member and defined date.

        Returns a dictionary containing the data from the retrieved row,
        or None if no row is retrieved.
        """
        
        row = self._execute_fetchone(
            """
            SELECT 
                staff_member_id,
                leave_date,
                leave_type
            FROM leave_bookings
            WHERE staff_member_id = ?
            AND leave_date = ?
            """,
            (staff_member_id, leave_date.strftime("%Y-%m-%d"))
        )
        return row

    def insert_leave_booking(self, staff_member_id: int, leave_date: date, leave_type: str | None = None):
        """
        Inserts a new record into the `leave_bookings` table.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            INSERT INTO leave_bookings
                (staff_member_id, leave_date, leave_type)
            VALUES
                (:staff_member_id, :leave_date, :leave_type) 
            """,
            {
                "staff_member_id": staff_member_id,
                "leave_date": leave_date.strftime("%Y-%m-%d"),
                "leave_type": leave_type
            }
        )

    def update_leave_booking(self, staff_member_id: int, leave_date: date, leave_type: str):
        """
        Updates all fields in the selected record in the `leave_bookings` table.

        At present, this is just the leave_type field, as all other fields are 
        part of the composite primary key, and so those should be modified by 
        deleting the record and adding a new one.

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
            UPDATE leave_bookings
            SET leave_type = ?
            WHERE staff_member_id = ?
            AND leave_date = ?
            """,
            (leave_type, staff_member_id, leave_date.strftime("%Y-%m-%d"))
        )
    

    def delete_leave_booking(self, staff_member_id: int, leave_date: date):
        """
        Delete a single record from the `leave_bookings` table identified by
        the staff_member_id / leave_date composite primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM leave_bookings
            WHERE staff_member_id = ?
            AND leave_date = ?
            """,
            (staff_member_id, leave_date)
        )

    # Flight hours logging functionality

    def get_flight_logs_by_staff_member_id(self, staff_member_id: int) -> list:
        """
        Retrieve all records (with all fields) from the `flight_time_logs` table
        for the defined staff member.

        Returns a list of dictionaries containing the data of each row returned.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                staff_member_id,
                effective_date,
                flight_hours
            FROM flight_time_logs
            WHERE staff_member_id = ?
            """,
            (staff_member_id, )
        )
        return rows
    
    def get_flight_log_record_by_staff_member_id_and_date(self, staff_member_id: int, effective_date: date) -> dict | None:
        """
        Retrieve a record (with all fields) from the `flight_time_logs` table
        for the defined staff member and defined date.

        Returns a dictionary containing the data from the retrieved row,
        or None if no row is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT
                staff_member_id,
                effective_date,
                flight_hours
            FROM flight_time_logs
            WHERE staff_member_id = ?
            AND effective_date = ?
            """,
            (staff_member_id, effective_date.strftime("%Y-%m-%d"))
        )
        return row

    def insert_flight_log_record(self, staff_member_id: int, effective_date: date, flight_hours: float):
        """
        Inserts a new record into the `flight_time_logs` table.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            INSERT INTO flight_time_logs
                (staff_member_id, effective_date, flight_hours)
            VALUES
                (:staff_member_id, :effective_date, :flight_hours) 
            """,
            {
                "staff_member_id": staff_member_id,
                "effective_date": effective_date.strftime("%Y-%m-%d"),
                "flight_hours": flight_hours
            }
        )

    def update_flight_log_record(self, staff_member_id: int, effective_date: date, flight_hours: float):
        """
        Updates all fields in the selected record in the `leave_bookings` table.
        
        At present, this is just the leave_type field, as all other fields are 
        part of the composite primary key, and so those should be modified by 
        deleting the record and adding a new one.

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
            UPDATE flight_time_logs
            SET flight_hours = ?
            WHERE staff_member_id = ?
            AND effective_date = ?
            """,
            (flight_hours, staff_member_id, effective_date.strftime("%Y-%m-%d"))
        )

    
    def delete_flight_log_record(self, staff_member_id: int, effective_date: date):
        """
        Delete a single record from the `flight_time_logs` table identified by
        the staff_member_id / effective_date composite primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM flight_time_logs
            WHERE staff_member_id = ?
            AND effective_date = ?
            """,
            (staff_member_id, effective_date.strftime("%Y-%m-%d"))
        )