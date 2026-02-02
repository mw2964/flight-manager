from flightmanagement.models.location import Location, Terminal, Gate

class LocationRepository:

    def __init__(self, conn):
        self.conn = conn

    # Core locations functionality

    def get_location_by_id(self, location_id: int) -> Location | None:        
        cursor = self.conn.execute(
            """
            SELECT *
            FROM locations
            WHERE location_id = ?
            """,
            (location_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_location(result)

    def get_location_by_code(self, code: str) -> Location | None:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM locations
            WHERE iata_airport_code = ?
            """,
            (code, )
        )
        result = cursor.fetchone()
        return self.dict_to_location(result)

    def get_location_list(self) -> list[Location]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM locations
            ORDER BY location_type desc, iata_airport_code
            """
        )
        results = cursor.fetchall()

        result_list = []
        for row in results:
            result_list.append(self.dict_to_location(row))

        return result_list

    def get_location_terminals(self, location_id) -> list[Terminal]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM terminals
            WHERE location_id = ?
            ORDER BY terminal_name
            """,
            (location_id, )
        )
        results = cursor.fetchall()

        result_list = []
        for row in results:
            result_list.append(self.dict_to_terminal(row))

        return result_list

    def insert_location(self, location: Location) -> None:        
        self.conn.execute(
            """
            INSERT INTO locations
                (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                (:location_type, :icao_location_code, :iata_airport_code, :location_name, :town_or_city, :state_or_county, :country, :geographic_region, :decimal_latitude, :decimal_longitude)
            """,
            location.to_dict()
        )

    def update_location(self, location: Location):
        self.conn.execute(
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
        self.conn.execute(
            """
            DELETE FROM locations
            WHERE location_id = ?
            """,
            (location.location_id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Location]:
        sql = f"""
            SELECT *
            FROM locations
            WHERE {field_name} = ?
            ORDER BY location_type, iata_airport_code
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(self.dict_to_location(row))

        return result_list
    
    def dict_to_location(self, data: dict | None) -> Location | None:
        if data is None or len(data) == 0:
            return None

        return Location(
            location_id=data["location_id"],
            location_type=data["location_type"],
            icao_location_code=data["icao_location_code"],
            iata_airport_code=data["iata_airport_code"],
            location_name=data["location_name"],
            town_or_city=data["town_or_city"],
            state_or_county=data["state_or_county"],
            country=data["country"],
            geographic_region=data["geographic_region"],
            decimal_latitude=data["decimal_latitude"],
            decimal_longitude=data["decimal_longitude"]
        )
    
    # Terminal functionality

    def get_terminal_by_id(self, terminal_id: int) -> Terminal | None:        
        cursor = self.conn.execute(
            """
            SELECT *
            FROM terminals
            WHERE terminal_id = ?
            """,
            (terminal_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_terminal(result)

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

    def get_terminal_gates(self, terminal_id) -> list[Gate]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM gates
            WHERE terminal_id = ?
            ORDER BY gate_number
            """,
            (terminal_id, )
        )
        results = cursor.fetchall()

        result_list = []
        for row in results:
            result_list.append(self.dict_to_gate(row))

        return result_list

    def insert_terminal(self, terminal: Terminal) -> None:        
        self.conn.execute(
            """
            INSERT INTO terminals
                (location_id, terminal_name)
            VALUES
                (:location_id, :terminal_name)
            """,
            terminal.to_dict()
        )

    def update_terminal(self, terminal: Terminal):
        self.conn.execute(
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
        self.conn.execute(
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
            terminal_id=data["terminal_id"],
            location_id=data["location_id"],
            terminal_name=data["terminal_name"]
        )
    

    # Gate functionality

    def get_gate_by_id(self, gate_id: int) -> Gate | None:        
        cursor = self.conn.execute(
            """
            SELECT *
            FROM gates
            WHERE gate_id = ?
            """,
            (gate_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_gate(result)

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

    def insert_gate(self, gate: Gate) -> None:        
        self.conn.execute(
            """
            INSERT INTO gates
                (terminal_id, gate_number)
            VALUES
                (:terminal_id, :gate_number)
            """,
            gate.to_dict()
        )

    def update_gate(self, gate: Gate):
        self.conn.execute(
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
        self.conn.execute(
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
            gate_id=data["gate_id"],
            terminal_id=data["terminal_id"],
            gate_number=data["gate_number"]
        )