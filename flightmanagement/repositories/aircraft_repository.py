from flightmanagement.models.aircraft import Aircraft

class AircraftRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_by_id(self, aircraft_id: int) -> Aircraft | None:

        cursor = self.conn.execute(
            """
            SELECT * FROM aircraft WHERE id = ?
            """,
            (aircraft_id, )
        )
        result = cursor.fetchone()
        
        if result is None or len(result) == 0:
            return None
        
        aircraft = Aircraft(
            result["id"],
            result["registration"],
            result["manufacturer_serial_no"],
            result["icao_hex"],
            result["manufacturer"],
            result["model"],
            result["icao_type"],
            result["status"]
        )
        return aircraft

    def get_by_registration(self, registration: str) -> Aircraft | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM aircraft WHERE registration = ?
            """,
            (registration, )
        )
        result = cursor.fetchone()
        
        if result is None or len(result) == 0:
            return None
        
        aircraft = Aircraft(
            result["id"],
            result["registration"],
            result["manufacturer_serial_no"],
            result["icao_hex"],
            result["manufacturer"],
            result["model"],
            result["icao_type"],
            result["status"]
        )
        return aircraft

    def get_aircraft_list(self) -> list[Aircraft] | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM aircraft ORDER BY registration
            """
        )
        results = cursor.fetchall()
        
        if results is None or len(results) == 0:
            return None
        
        result_list = []
        for row in results:
            result_list.append(
                Aircraft(
                    row["id"],
                    row["registration"],
                    row["manufacturer_serial_no"],
                    row["icao_hex"],
                    row["manufacturer"],
                    row["model"],
                    row["icao_type"],
                    row["status"]
                )
            )

        return result_list

    def add_aircraft(self, aircraft: Aircraft) -> None:        
        data = {
            "registration": aircraft.registration, 
            "manufacturer_serial_no": aircraft.manufacturer_serial_no,
            "icao_hex": aircraft.icao_hex, 
            "manufacturer": aircraft.manufacturer,
            "model": aircraft.model,
            "icao_type": aircraft.icao_type,
            "status": aircraft.status
        }

        self.conn.execute(
            """
            INSERT INTO aircraft
                (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
            VALUES
                (:registration, :manufacturer_serial_no, :icao_hex, :manufacturer, :model, :icao_type, :status)
            """,
            data
        )

    def update_aircraft(self, aircraft: Aircraft):
        self.conn.execute(
            """
            UPDATE aircraft
            SET
                registration = ?,
                manufacturer_serial_no = ?,
                icao_hex = ?,
                manufacturer = ?,
                model = ?,
                icao_type = ?,
                status = ?
            WHERE id = ?
            """,
            (aircraft.registration, aircraft.manufacturer_serial_no, aircraft.icao_hex, aircraft.manufacturer, aircraft.model, aircraft.icao_type, aircraft.status, aircraft.id)
        )
    
    def delete_aircraft(self, aircraft_id: int):
        self.conn.execute(
            """
            DELETE FROM aircraft
            WHERE id = ?
            """,
            (aircraft_id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Aircraft] | None:
        sql = f"""
            SELECT *
            FROM aircraft
            WHERE {field_name} = ?
            ORDER BY registration
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        if results is None or len(results) == 0:
            return None

        result_list = []
        for row in results:
            result_list.append(
                Aircraft(
                    row["id"],
                    row["registration"],
                    row["manufacturer_serial_no"],
                    row["icao_hex"],
                    row["manufacturer"],
                    row["model"],
                    row["icao_type"],
                    row["status"]
                )
            )

        return result_list
    