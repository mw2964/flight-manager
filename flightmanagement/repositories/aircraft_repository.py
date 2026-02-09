from flightmanagement.models.aircraft import Aircraft, AircraftType
from flightmanagement.repositories.base_repository import BaseRepository

class AircraftRepository(BaseRepository):

    def __init__(self, conn):
        super().__init__(conn)

    # Core aircraft functionality

    def get_aircraft_by_id(self, aircraft_id: int) -> Aircraft | None:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM aircraft
            WHERE aircraft_id = ?
            """,
            (aircraft_id, )
        )    
        return self.dict_to_aircraft(row)

    def get_aircraft_by_registration(self, registration: str) -> Aircraft | None:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM aircraft
            WHERE registration = ?
            """,
            (registration, )
        )
        return self.dict_to_aircraft(row)

    def get_aircraft_list(self) -> list[Aircraft]:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM vw_aircraft
            ORDER BY registration
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_aircraft(row))

        return result_list

    def search_aircraft_on_field(self, field_name: str, value) -> list[Aircraft]:
        sql = f"""
            SELECT *
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
        return row["aircraft_id"]
        
    def update_aircraft(self, aircraft: Aircraft):
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
        self._execute(
            """
            DELETE FROM aircraft
            WHERE aircraft_id = ?
            """,
            (aircraft.aircraft_id, )
        )
    
    def dict_to_aircraft(self, data: dict | None) -> Aircraft | None:
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

    # Aircraft type functionality

    def get_aircraft_type_by_id(self, aircraft_type_id: int) -> AircraftType | None:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM aircraft_types
            WHERE aircraft_type_id = ?
            """,
            (aircraft_type_id, )
        )      
        return self.dict_to_aircraft_type(row)

    def get_aircraft_type_by_model(self, model: str) -> AircraftType | None:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM aircraft_types
            WHERE model = ?
            """,
            (model, )
        )
        return self.dict_to_aircraft_type(row)
        
    def get_aircraft_type_list(self) -> list:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM aircraft_types
            ORDER BY manufacturer, model
            """
        )
        return rows

    def insert_aircraft_type(self, aircraft_type: AircraftType) -> None:        
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
        return row["aircraft_type_id"]

    def update_aircraft_type(self, aircraft_type: AircraftType):
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
        self._execute(
            """
            DELETE FROM aircraft_types
            WHERE aircraft_type_id = ?
            """,
            (aircraft_type.aircraft_type_id, )
        )
    
    def dict_to_aircraft_type(self, data: dict | None) -> AircraftType | None:
        if data is None or len(data) == 0:
            return None

        return AircraftType(
            aircraft_type_id = data["aircraft_type_id"],
            manufacturer = data["manufacturer"],
            model = data["model"],
            icao_type = data["icao_type"]
        )
