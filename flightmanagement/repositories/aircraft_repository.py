from flightmanagement.models.aircraft import Aircraft

class AircraftRepository:

    ALLOWED_SEARCH_FIELDS = {
        'registration',
        'manufacturer_serial_no',
        'icao_hex',
        'manufacturer',
        'model',
        'icao_type',
        'status'
    }

    def __init__(self, conn):
        self.conn = conn

    def get_item_by_id(self, aircraft_id: int) -> Aircraft | None:

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
            id=result["id"],
            registration=result["registration"],
            manufacturer_serial_no=result["manufacturer_serial_no"],
            icao_hex=result["icao_hex"],
            manufacturer=result["manufacturer"],
            model=result["model"],
            icao_type=result["icao_type"],
            status=result["status"]
        )
        return aircraft

    def get_item_by_registration(self, registration: str) -> Aircraft | None:
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
            id=result["id"],
            registration=result["registration"],
            manufacturer_serial_no=result["manufacturer_serial_no"],
            icao_hex=result["icao_hex"],
            manufacturer=result["manufacturer"],
            model=result["model"],
            icao_type=result["icao_type"],
            status=result["status"]
        )
        return aircraft

    def get_aircraft_list(self) -> list[Aircraft]:
        cursor = self.conn.execute(
            """
            SELECT * FROM aircraft ORDER BY registration
            """
        )
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(
                Aircraft(
                    id=row["id"],
                    registration=row["registration"],
                    manufacturer_serial_no=row["manufacturer_serial_no"],
                    icao_hex=row["icao_hex"],
                    manufacturer=row["manufacturer"],
                    model=row["model"],
                    icao_type=row["icao_type"],
                    status=row["status"]
                )
            )

        return result_list

    def insert_item(self, aircraft: Aircraft) -> None:        
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

    def update_item(self, aircraft: Aircraft):
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
    
    def delete_item(self, aircraft: Aircraft):
        self.conn.execute(
            """
            DELETE FROM aircraft
            WHERE id = ?
            """,
            (aircraft.id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Aircraft]:
        
        if field_name not in self.ALLOWED_SEARCH_FIELDS:
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
            result_list.append(
                Aircraft(
                    id=row["id"],
                    registration=row["registration"],
                    manufacturer_serial_no=row["manufacturer_serial_no"],
                    icao_hex=row["icao_hex"],
                    manufacturer=row["manufacturer"],
                    model=row["model"],
                    icao_type=row["icao_type"],
                    status=row["status"]
                )
            )

        return result_list
    