from flightmanagement.error import RepositoryError
from flightmanagement.models.aircraft import Aircraft, AircraftType
from flightmanagement.repositories.base_repository import BaseRepository

class AircraftRepository(BaseRepository):
    """
    Repository responsible for all database operations related to aircraft
    and aircraft types.

    This class provides CRUD functionality for Aircraft and AircraftType domain
    objects, encapsulating all SQL access and database interactions. It includes
    methods to retrieve aircraft by different criteria, and to insert, update,
    and delete aircraft records. It also manages aircraft type lookups and maintenance.

    The repository maps database rows to domain models and relies on the
    BaseRepository class for connection handling, query execution and exception handling.
    """

    def __init__(self, conn):
        super().__init__(conn)

    """
    Aircraft functionality
    """

    def get_aircraft_by_id(self, aircraft_id: int) -> Aircraft | None:
        """
        Retrieve a single record (with all fields) from the `aircraft` table
        using the aircraft_id primary key.

        Returns an Aircraft object constructed from the returned record, 
        or None if no record is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT
                aircraft_id,
                aircraft_type_id,
                registration,
                manufacturer_serial_no,
                icao_hex,
                aircraft_status
            FROM aircraft
            WHERE aircraft_id = ?
            """,
            (aircraft_id, )
        )    
        return self.dict_to_aircraft(row)

    def get_aircraft_list(self) -> list[Aircraft]:
        """
        Retrieve all records (with all fields) from the `aircraft` table.

        Returns a list of Aircraft objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                aircraft_id,
                aircraft_type_id,
                registration,
                manufacturer_serial_no,
                icao_hex,
                aircraft_status
            FROM aircraft
            ORDER BY registration
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_aircraft(row))

        return result_list
    
    def get_active_aircraft_list(self) -> list[Aircraft]:
        """
        Retrieve all records (with all fields) from the `aircraft` table representing active aircraft.

        Returns a list of Aircraft objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                aircraft_id,
                aircraft_type_id,
                registration,
                manufacturer_serial_no,
                icao_hex,
                aircraft_status
            FROM aircraft
            WHERE aircraft_status = 'Active'
            ORDER BY registration
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_aircraft(row))

        return result_list

    def search_aircraft_on_field(self, field_name: str, value) -> list[Aircraft]:
        """
        Retrieve all records (with all fields) from the denormalised view over the `aircraft`
        and `aircraft_type` tables where the provided field name has the provided value.

        This is intended to reduce code duplication by enabling searching against any
        single field in the same method, by injecting the field name into the SQL query.
        Inappropriate SQL injection is guarded against by restricting the allowed values
        for the field_name parameter.

        Returns a list of Aircraft objects constructed from the returned records.
        """

        # Limit the values that can be entered as field_name
        # to mitigate SQL injection risk
        allowed_search_fields = {
            "aircraft_id",
            "aircraft_type_id",
            "registration",
            "manufacturer_serial_no",
            "icao_hex",
            "aircraft_status",
            "manufacturer",
            "model",
            "icao_type"
        }
        if field_name not in allowed_search_fields:
            raise RepositoryError("Invalid search field")

        sql = f"""
            SELECT
                aircraft_id,
                aircraft_type_id,
                registration,
                manufacturer_serial_no,
                icao_hex,
                aircraft_status,
                manufacturer,
                model,
                icao_type
            FROM vw_aircraft
            WHERE {field_name} = ?
            ORDER BY registration
        """
        rows = self._execute_fetchall(sql, (value, ))
        result_list = []
        for row in rows:
            result_list.append(self.dict_to_aircraft(row))

        return result_list

    def insert_aircraft(self, aircraft: Aircraft) -> int:
        """
        Inserts a new record into the `aircraft` table.

        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement aircraft_id primary key minted by the database
        for the new record.
        """

        row = self._execute_fetchone(
            """
            INSERT INTO aircraft
                (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (:aircraft_type_id, :registration, :manufacturer_serial_no, :icao_hex, :aircraft_status)
            RETURNING aircraft_id
            """,
            {
                "aircraft_type_id": aircraft.aircraft_type_id,
                "registration": aircraft.registration, 
                "manufacturer_serial_no": aircraft.manufacturer_serial_no,
                "icao_hex": aircraft.icao_hex,
                "aircraft_status": aircraft.aircraft_status
            }
        )
        if row is None:
            raise RepositoryError("Failed to insert aircraft.")
        return row["aircraft_id"]
        
    def update_aircraft(self, aircraft: Aircraft):
        """
        Updates all fields in the selected record in the `aircraft` table.

        Field values are derived from the attributes of the Aircraft object.
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
            UPDATE aircraft
            SET
                aircraft_type_id = ?,
                registration = ?,
                manufacturer_serial_no = ?,
                icao_hex = ?,
                aircraft_status = ?
            WHERE aircraft_id = ?
            """,
            (
                aircraft.aircraft_type_id,
                aircraft.registration,
                aircraft.manufacturer_serial_no,
                aircraft.icao_hex,
                aircraft.aircraft_status,
                aircraft.aircraft_id
            )
        )
    
    def delete_aircraft(self, aircraft: Aircraft):
        """
        Delete a single record from the `aircraft` table identified by
        the aircraft_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM aircraft
            WHERE aircraft_id = ?
            """,
            (aircraft.aircraft_id, )
        )
    
    def dict_to_aircraft(self, data: dict | None) -> Aircraft | None:
        """
        Create and populate the attributes of an Aircraft object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Aircraft domain model, and violations raised as domain model
        exceptions.

        Returns the Aircraft object, or None if the dictionary is missing or
        empty. 
        """

        if data is None or len(data) == 0:
            return None

        return Aircraft(
            aircraft_id = data["aircraft_id"],
            aircraft_type_id = data["aircraft_type_id"],
            registration = data["registration"],
            manufacturer_serial_no = data["manufacturer_serial_no"],
            icao_hex = data["icao_hex"],
            aircraft_status = data["aircraft_status"]
        )

    """
    Aircraft type functionality
    """

    def get_aircraft_type_by_id(self, aircraft_type_id: int) -> AircraftType | None:
        """
        Retrieve a single record (with all fields) from the `aircraft_type` table
        using the aircraft_type_id primary key.

        Returns an AircraftType object constructed from the returned record, 
        or None if no record is retrieved.
        """
                
        row = self._execute_fetchone(
            """
            SELECT
                aircraft_type_id,
                manufacturer,
                model,
                icao_type
            FROM aircraft_types
            WHERE aircraft_type_id = ?
            """,
            (aircraft_type_id, )
        )      
        return self.dict_to_aircraft_type(row)
        
    def get_aircraft_type_list(self) -> list:
        """
        Retrieve all records (with all fields) from the `aircraft_type` table.

        Returns a list of AircraftType objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                aircraft_type_id,
                manufacturer,
                model,
                icao_type
            FROM aircraft_types
            ORDER BY manufacturer, model
            """
        )
        return rows

    def insert_aircraft_type(self, aircraft_type: AircraftType) -> None:
        """
        Inserts a new record into the `aircraft_type` table.

        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement aircraft_type_id primary key minted by the database
        for the new record.
        """

        row = self._execute_fetchone(
            """
            INSERT INTO aircraft_types
                (manufacturer, model, icao_type)
            VALUES
                (:manufacturer, :model, :icao_type)
            RETURNING aircraft_type_id
            """,
            {
                "manufacturer": aircraft_type.manufacturer,
                "model": aircraft_type.model, 
                "icao_type": aircraft_type.icao_type
            }
        )
        if row is None:
            raise RepositoryError("Failed to insert aircraft type.")
        return row["aircraft_type_id"]

    def update_aircraft_type(self, aircraft_type: AircraftType):
        """
        Updates all fields in the selected record in the `aircraft_type` table.

        Field values are derived from the attributes of the AircraftType object.
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
            UPDATE aircraft_types
            SET
                manufacturer = ?,
                model = ?,
                icao_type = ?
            WHERE aircraft_type_id = ?
            """,
            (
                aircraft_type.manufacturer,
                aircraft_type.model,
                aircraft_type.icao_type,
                aircraft_type.aircraft_type_id
            )
        )

    def delete_aircraft_type(self, aircraft_type: AircraftType):
        """
        Delete a single record from the `aircraft_type` table identified by
        the aircraft_type_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM aircraft_types
            WHERE aircraft_type_id = ?
            """,
            (aircraft_type.aircraft_type_id, )
        )
    
    def dict_to_aircraft_type(self, data: dict | None) -> AircraftType | None:
        """
        Create and populate the attributes of an Aircraft object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Aircraft domain model, and violations raised as domain model
        exceptions.

        Returns the Aircraft object, or None if the dictionary is missing or
        empty. 
        """
        
        if data is None or len(data) == 0:
            return None

        return AircraftType(
            aircraft_type_id = data["aircraft_type_id"],
            manufacturer = data["manufacturer"],
            model = data["model"],
            icao_type = data["icao_type"]
        )
