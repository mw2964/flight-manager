from flightmanagement.models.location import Location

class LocationRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_item_by_id(self, location_id: int) -> Location | None:        
        cursor = self.conn.execute(
            """
            SELECT *
            FROM locations
            WHERE id = ?
            """,
            (location_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_location(result)

    def get_item_by_code(self, code: str) -> Location | None:
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
            SELECT * FROM locations
            ORDER BY location_type desc, iata_airport_code
            """
        )
        results = cursor.fetchall()

        result_list = []
        for row in results:
            result_list.append(self.dict_to_location(row))

        return result_list

    def insert_item(self, location: Location) -> None:        
        self.conn.execute(
            """
            INSERT INTO locations
                (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                (:location_type, :icao_location_code, :iata_airport_code, :location_name, :town_or_city, :state_or_county, :country, :geographic_region, :decimal_latitude, :decimal_longitude)
            """,
            location.to_dict()
        )

    def update_item(self, location: Location):
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
    
    def delete_item(self, location: Location):
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