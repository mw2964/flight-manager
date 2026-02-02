from flightmanagement.models.aircraft import Aircraft, AircraftType

class AircraftRepository:

    AIRCRAFT_SEARCH_FIELDS = {
        'aircraft_type_id',
        'registration',
        'manufacturer_serial_no',
        'icao_hex',
        'aircraft_status'
    }

    AIRCRAFT_TYPE_SEARCH_FIELDS = {
        'manufacturer',
        'model',
        'icao_type'
    }

    def __init__(self, conn):
        self.conn = conn

    # Core aircraft functionality

    def get_aircraft_by_id(self, aircraft_id: int) -> Aircraft | None:

        cursor = self.conn.execute(
            """
            SELECT *
            FROM aircraft
            WHERE aircraft_id = ?
            """,
            (aircraft_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_aircraft(result)

    def get_aircraft_by_registration(self, registration: str) -> Aircraft | None:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM aircraft
            WHERE registration = ?
            """,
            (registration, )
        )
        result = cursor.fetchone()
        
        return self.dict_to_aircraft(result)

    def get_aircraft_list(self) -> list[Aircraft]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM aircraft
            ORDER BY registration
            """
        )
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(
                self.dict_to_aircraft(row)
            )

        return result_list

    def insert_aircraft(self, aircraft: Aircraft) -> None:        
        self.conn.execute(
            """
            INSERT INTO aircraft
                (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
            VALUES
                (:registration, :manufacturer_serial_no, :icao_hex, :manufacturer, :model, :icao_type, :status)
            """,
            aircraft.to_dict()
        )

    def update_aircraft(self, aircraft: Aircraft):
        self.conn.execute(
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
        self.conn.execute(
            """
            DELETE FROM aircraft
            WHERE aircraft_id = ?
            """,
            (aircraft.aircraft_id, )
        )
    
    def search_aircraft_on_field(self, field_name: str, value) -> list[Aircraft]:
        
        if field_name not in self.AIRCRAFT_SEARCH_FIELDS:
            raise ValueError(f"Invalid search field: {field_name}")

        sql = f"""
            SELECT *
            FROM aircraft
            WHERE {field_name} = ?
            ORDER BY registration
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(self.dict_to_aircraft(row))

        return result_list
    
    def dict_to_aircraft(self, data: dict | None) -> Aircraft | None:
        if data is None or len(data) == 0:
            return None

        return Aircraft(
            aircraft_id=data["aircraft_id"],
            aircraft_type_id=data["aircraft_type_id"],
            registration=data["registration"],
            manufacturer_serial_no=data["manufacturer_serial_no"],
            icao_hex=data["icao_hex"],
            aircraft_status=data["aircraft_status"]
        )

    # Aircraft type functionality

    def get_aircraft_type_by_id(self, aircraft_type_id: int) -> AircraftType | None:

        cursor = self.conn.execute(
            """
            SELECT *
            FROM aircraft_type
            WHERE aircraft_type_id = ?
            """,
            (aircraft_type_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_aircraft_type(result)

    def get_aircraft_type_by_model(self, model: str) -> AircraftType | None:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM aircraft_type
            WHERE model = ?
            """,
            (model, )
        )
        result = cursor.fetchone()
        
        return self.dict_to_aircraft_type(result)

    def get_aircraft_type_list(self) -> list[AircraftType]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM aircraft_type
            ORDER BY manufacturer, model
            """
        )
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(
                self.dict_to_aircraft_type(row)
            )

        return result_list

    def insert_aircraft_type(self, aircraft_type: AircraftType) -> None:        
        self.conn.execute(
            """
            INSERT INTO aircraft_type
                (manufacturer, model, icao_type)
            VALUES
                (:manufacturer, :model, :icao_type)
            """,
            aircraft_type.to_dict()
        )

    def update_aircraft_type(self, aircraft_type: AircraftType):
        self.conn.execute(
            """
            UPDATE aircraft_type
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
        self.conn.execute(
            """
            DELETE FROM aircraft_type
            WHERE aircraft_type_id = ?
            """,
            (aircraft_type.aircraft_type_id, )
        )
    
    def search_aircraft_type_on_field(self, field_name: str, value) -> list[AircraftType]:
        
        if field_name not in self.AIRCRAFT_TYPE_SEARCH_FIELDS:
            raise ValueError(f"Invalid search field: {field_name}")

        sql = f"""
            SELECT *
            FROM aircraft_type
            WHERE {field_name} = ?
            ORDER BY manufacturer, model
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(self.dict_to_aircraft_type(row))

        return result_list
    
    def dict_to_aircraft_type(self, data: dict | None) -> AircraftType | None:
        if data is None or len(data) == 0:
            return None

        return AircraftType(
            aircraft_type_id=data["aircraft_type_id"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            icao_type=data["icao_type"]
        )