from flightmanagement.models.location import Location, Terminal, Gate
from flightmanagement.repositories.base_repository import BaseRepository

class LocationRepository(BaseRepository):

    LOCATION_SEARCH_FIELDS = {
        'location_type', 
        'icao_location_code',
        'iata_airport_code', 
        'location_name',
        'town_or_city',
        'state_or_county',
        'country',
        'geographic_region',
        'decimal_latitude',
        'decimal_longitude'
    }

    def __init__(self, conn):
        super().__init__(conn)

    # Core locations functionality

    def get_location_by_id(self, location_id: int) -> Location | None:        
        row = self._execute_fetchone(
            """
            SELECT *
            FROM locations
            WHERE location_id = ?
            """,
            (location_id, )
        )    
        return self.dict_to_location(row)

    def get_location_by_code(self, code: str) -> Location | None:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM locations
            WHERE iata_airport_code = ?
            """,
            (code, )
        )
        return self.dict_to_location(row)

    def get_location_list(self) -> list[Location]:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM locations
            ORDER BY location_type desc, iata_airport_code
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_location(row))

        return result_list

    def search_on_field(self, field_name: str, value) -> list[Location]:
        if field_name not in self.LOCATION_SEARCH_FIELDS:
            raise ValueError(f"Invalid search field: {field_name}")

        sql = f"""
            SELECT *
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
        rows = self._execute_fetchall(
            """
            SELECT *
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
        return row["location_id"]

    def update_location(self, location: Location):
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
        self._execute(
            """
            DELETE FROM locations
            WHERE location_id = ?
            """,
            (location.location_id, )
        )
    
    def dict_to_location(self, data: dict | None) -> Location | None:
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
        row = self._execute_fetchone(
            """
            SELECT *
            FROM terminals
            WHERE terminal_id = ?
            """,
            (terminal_id, )
        )      
        return self.dict_to_terminal(row)

    '''
    def get_terminal_by_name(self, terminal_name: str) -> Terminal | None:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM terminals
            WHERE terminal_name = ?
            """,
            (terminal_name, )
        )
        result = cursor.fetchone()
        return self.dict_to_terminal(result)
    '''
        
    def get_terminal_gates(self, terminal_id) -> list[Gate]:
        rows = self._execute_fetchall(
            """
            SELECT *
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

    def insert_terminal(self, terminal: Terminal) -> None:        
        self._execute(
            """
            INSERT INTO terminals
                (location_id, terminal_name)
            VALUES
                (:location_id, :terminal_name)
            """,
            terminal.to_dict()
        )

    def update_terminal(self, terminal: Terminal):
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
        self._execute(
            """
            DELETE FROM terminals
            WHERE terminal_id = ?
            """,
            (terminal.terminal_id, )
        )

    def dict_to_terminal(self, data: dict | None) -> Terminal | None:
        if data is None or len(data) == 0:
            return None

        return Terminal(
            terminal_id = data["terminal_id"],
            location_id = data["location_id"],
            terminal_name = data["terminal_name"]
        )
    

    # Gate functionality

    def get_gate_by_id(self, gate_id: int) -> Gate | None:        
        row = self._execute_fetchone(
            """
            SELECT *
            FROM gates
            WHERE gate_id = ?
            """,
            (gate_id, )
        )     
        return self.dict_to_gate(row)

    '''
    def get_gate_by_number(self, gate_number: str) -> Gate | None:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM gates
            WHERE gate_number = ?
            """,
            (gate_number, )
        )
        result = cursor.fetchone()
        return self.dict_to_gate(result)
    '''
        
    def insert_gate(self, gate: Gate) -> None:        
        self._execute(
            """
            INSERT INTO gates
                (terminal_id, gate_number)
            VALUES
                (:terminal_id, :gate_number)
            """,
            gate.to_dict()
        )

    def update_gate(self, gate: Gate):
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
        self._execute(
            """
            DELETE FROM gates
            WHERE gate_id = ?
            """,
            (gate.gate_id, )
        )

    def dict_to_gate(self, data: dict | None) -> Gate | None:
        if data is None or len(data) == 0:
            return None

        return Gate(
            gate_id = data["gate_id"],
            terminal_id = data["terminal_id"],
            gate_number = data["gate_number"]
        )