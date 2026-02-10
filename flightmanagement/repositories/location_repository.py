from flightmanagement.error import RepositoryError
from flightmanagement.models.location import Location, Terminal, Gate
from flightmanagement.repositories.base_repository import BaseRepository

class LocationRepository(BaseRepository):
    """
    Repository responsible for all database operations related to locations
    (airports, airfields etc) and their child terminals and gates.

    This class provides CRUD functionality for Location, Terminal and Gate domain objects,
    encapsulating all SQL access and database interactions. It includes
    methods to retrieve locations, terminals and gates by different criteria, and to insert, update,
    and delete location, terminal and gate records.

    The repository maps database rows to domain models and relies on the
    BaseRepository class for connection handling, query execution and exception handling.
    """

    def __init__(self, conn):
        super().__init__(conn)

    """
    Core locations functionality
    """

    def get_location_by_id(self, location_id: int) -> Location | None:
        """
        Retrieve a single record (with all fields) from the `location` table
        using the location_id primary key.

        Returns a Location object constructed from the returned record, 
        or None if no record is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT
                location_id,
                location_type, 
                icao_location_code,
                iata_airport_code, 
                location_name,
                town_or_city,
                state_or_county,
                country,
                geographic_region,
                decimal_latitude,
                decimal_longitude
            FROM locations
            WHERE location_id = ?
            """,
            (location_id, )
        )    
        return self.dict_to_location(row)

    def get_location_list(self) -> list[Location]:
        """
        Retrieve all records (with all fields) from the `locations` table.

        Returns a list of Location objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                location_id,
                location_type, 
                icao_location_code,
                iata_airport_code, 
                location_name,
                town_or_city,
                state_or_county,
                country,
                geographic_region,
                decimal_latitude,
                decimal_longitude
            FROM locations
            ORDER BY location_type desc, iata_airport_code
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_location(row))

        return result_list

    def search_on_field(self, field_name: str, value) -> list[Location]:
        """
        Retrieve all records (with all fields) from `locations` tablee where
        the provided field name has the provided value.

        This is intended to reduce code duplication by enabling searching against any
        single field in the same method, by injecting the field name into the SQL query.
        Inappropriate SQL injection is guarded against by restricting the allowed values
        for the field_name parameter.

        Returns a list of Location objects constructed from the returned records.
        """

        # Restrict the values that can be entered into field_name to protect from SQL injection
        allowed_search_fields = {
            "location_id",
            "location_type", 
            "icao_location_code",
            "iata_airport_code", 
            "location_name",
            "town_or_city",
            "state_or_county",
            "country",
            "geographic_region",
            "decimal_latitude",
            "decimal_longitude"
        }

        if field_name not in allowed_search_fields:
            raise RepositoryError(f"Invalid search field: {field_name}")

        sql = f"""
            SELECT
                location_id,
                location_type, 
                icao_location_code,
                iata_airport_code, 
                location_name,
                town_or_city,
                state_or_county,
                country,
                geographic_region,
                decimal_latitude,
                decimal_longitude
            FROM locations
            WHERE {field_name} = ?
            ORDER BY location_type, iata_airport_code
        """
        rows = self._execute_fetchall(sql, (value, ))
        
        result_list = []
        for row in rows:
            result_list.append(self.dict_to_location(row))

        return result_list

    def get_location_terminals(self, location_id) -> list[Terminal]:
        """
        Retrieve all records (with all fields) from the `terminals` table that
        are linked to the specified location.

        Returns a list of Terminal objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                terminal_id,
                location_id,
                terminal_name
            FROM terminals
            WHERE location_id = ?
            ORDER BY terminal_name
            """,
            (location_id, )
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_terminal(row))

        return result_list

    def insert_location(self, location: Location) -> int:
        """
        Inserts a new record into the `locations` table.

        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement location_id primary key minted by the database
        for the new record.
        """

        row = self._execute_fetchone(
            """
            INSERT INTO locations
                (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                (:location_type, :icao_location_code, :iata_airport_code, :location_name, :town_or_city, :state_or_county, :country, :geographic_region, :decimal_latitude, :decimal_longitude)
            RETURNING location_id
            """,
            {
                "location_type": location.location_type, 
                "icao_location_code": location.icao_location_code,
                "iata_airport_code": location.iata_airport_code, 
                "location_name": location.location_name,
                "town_or_city": location.town_or_city,
                "state_or_county": location.state_or_county,
                "country": location.country,
                "geographic_region": location.geographic_region,
                "decimal_latitude": location.decimal_latitude,
                "decimal_longitude": location.decimal_longitude
            }
        )
        if row is None:
            raise RepositoryError("Failed to insert location.")
        return row["location_id"]

    def update_location(self, location: Location):
        """
        Updates all fields in the selected record in the `locations` table.

        Field values are derived from the attributes of the Location object.
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
            UPDATE locations
            SET
                location_type = ?, 
                icao_location_code = ?, 
                iata_airport_code = ?, 
                location_name = ?, 
                town_or_city = ?, 
                state_or_county = ?, 
                country = ?, 
                geographic_region = ?, 
                decimal_latitude = ?, 
                decimal_longitude = ?
            WHERE location_id = ?
            """,
            (
                location.location_type, 
                location.icao_location_code,
                location.iata_airport_code, 
                location.location_name,
                location.town_or_city,
                location.state_or_county,
                location.country,
                location.geographic_region,
                location.decimal_latitude,
                location.decimal_longitude,
                location.location_id
            )
        )
    
    def delete_location(self, location: Location):
        """
        Delete a single record from the `locations` table identified by
        the location_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM locations
            WHERE location_id = ?
            """,
            (location.location_id, )
        )
    
    def dict_to_location(self, data: dict | None) -> Location | None:
        """
        Create and populate the attributes of a Location object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Location domain model, and violations raised as domain model
        exceptions.

        Returns the Location object, or None if the dictionary is missing or
        empty. 
        """

        if data is None or len(data) == 0:
            return None

        return Location(
            location_id = data["location_id"],
            location_type = data["location_type"],
            icao_location_code = data["icao_location_code"],
            iata_airport_code = data["iata_airport_code"],
            location_name = data["location_name"],
            town_or_city = data["town_or_city"],
            state_or_county = data["state_or_county"],
            country = data["country"],
            geographic_region = data["geographic_region"],
            decimal_latitude = data["decimal_latitude"],
            decimal_longitude = data["decimal_longitude"]
        )
    
    # Terminal functionality

    def get_terminal_by_id(self, terminal_id: int) -> Terminal | None:
        """
        Retrieve a single record (with all fields) from the `terminals` table
        using the terminal_id primary key.

        Returns a Terminal object constructed from the returned record, 
        or None if no record is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT
                terminal_id,
                location_id,
                terminal_name
            FROM terminals
            WHERE terminal_id = ?
            """,
            (terminal_id, )
        )      
        return self.dict_to_terminal(row)

    def get_terminal_gates(self, terminal_id) -> list[Gate]:
        """
        Retrieve all records (with all fields) from the `gates` table that
        are linked to the specified terminal.

        Returns a list of Gate objects constructed from the returned records, or an empty list if
        no records are retrieved.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                gate_id,
                terminal_id,
                gate_number
            FROM gates
            WHERE terminal_id = ?
            ORDER BY gate_number
            """,
            (terminal_id, )
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_gate(row))

        return result_list

    def insert_terminal(self, terminal: Terminal) -> int:
        """
        Inserts a new record into the `terminals` table.

        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement terminal_id primary key minted by the database
        for the new record.
        """

        row = self._execute_fetchone(
            """
            INSERT INTO terminals
                (location_id, terminal_name)
            VALUES
                (:location_id, :terminal_name)
            RETURNING terminal_id
            """,
            terminal.to_dict()
        )
        if row is None:
            raise RepositoryError("Failed to insert terminal.")
        return row["terminal_id"]

    def update_terminal(self, terminal: Terminal):
        """
        Updates all fields in the selected record in the `terminals` table.

        Field values are derived from the attributes of the Terminal object.
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
            UPDATE terminals
            SET
                terminal_name = ?
            WHERE terminal_id = ?
            """,
            (
                terminal.terminal_name, 
                terminal.terminal_id
            )
        )
    
    def delete_terminal(self, terminal: Terminal):
        """
        Delete a single record from the `terminals` table identified by
        the terminal_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM terminals
            WHERE terminal_id = ?
            """,
            (terminal.terminal_id, )
        )

    def dict_to_terminal(self, data: dict | None) -> Terminal | None:
        """
        Create and populate the attributes of a Terminal object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Terminal domain model, and violations raised as domain model
        exceptions.

        Returns the Terminal object, or None if the dictionary is missing or
        empty. 
        """

        if data is None or len(data) == 0:
            return None

        return Terminal(
            terminal_id = data["terminal_id"],
            location_id = data["location_id"],
            terminal_name = data["terminal_name"]
        )
    

    # Gate functionality

    def get_gate_by_id(self, gate_id: int) -> Gate | None:
        """
        Retrieve a single record (with all fields) from the `gates` table
        using the gate_id primary key.

        Returns a Gate object constructed from the returned record, 
        or None if no record is retrieved.
        """

        row = self._execute_fetchone(
            """
            SELECT *
            FROM gates
            WHERE gate_id = ?
            """,
            (gate_id, )
        )     
        return self.dict_to_gate(row)
        
    def insert_gate(self, gate: Gate) -> None:
        """
        Inserts a new record into the `gates` table.

        Unpopulated parameters will have default values assigned according to
        the database schema.

        Any database constraint violations (e.g. unique key constraints) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.

        Returns the autoincrement gate_id primary key minted by the database
        for the new record.
        """

        row = self._execute_fetchone(
            """
            INSERT INTO gates
                (terminal_id, gate_number)
            VALUES
                (:terminal_id, :gate_number)
            RETURNING gate_id
            """,
            gate.to_dict()
        )
        if row is None:
            raise RepositoryError("Failed to insert gate.")
        return row["gate_id"]

    def update_gate(self, gate: Gate):
        """
        Updates all fields in the selected record in the `gates` table.

        Field values are derived from the attributes of the Gate object.
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
            UPDATE gates
            SET
                gate_number = ?
            WHERE gate_id = ?
            """,
            (
                gate.gate_number, 
                gate.gate_id
            )
        )
    
    def delete_gate(self, gate: Gate):
        """
        Delete a single record from the `gates` table identified by
        the gate_id primary key.

        Any database constraint violations (e.g. dependent records) will
        be caught and handled by the BaseRepository class, and the
        transaction rolled back by the transaction context manager in 
        the db module.
        """

        self._execute(
            """
            DELETE FROM gates
            WHERE gate_id = ?
            """,
            (gate.gate_id, )
        )

    def dict_to_gate(self, data: dict | None) -> Gate | None:
        """
        Create and populate the attributes of a Gate object from the
        dictionary of key-value pairs provided.

        Single attribute and cross-attribute validations will be carried out
        by the Gate domain model, and violations raised as domain model
        exceptions.

        Returns the Gate object, or None if the dictionary is missing or
        empty. 
        """

        if data is None or len(data) == 0:
            return None

        return Gate(
            gate_id = data["gate_id"],
            terminal_id = data["terminal_id"],
            gate_number = data["gate_number"]
        )