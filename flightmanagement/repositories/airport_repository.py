from flightmanagement.models.airport import Airport

class AirportRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_by_id(self, airport_id: int) -> Airport | None:        
        cursor = self.conn.execute(
            """
            SELECT * FROM airport WHERE id = ?
            """,
            (airport_id, )
        )
        result = cursor.fetchone()
        
        if result is None or len(result) == 0:
            return None

        airport = Airport(
            result["id"],
            result["code"],
            result["name"],
            result["city"],
            result["country"],
            result["region"]
        )
        return airport

    def get_by_code(self, code: str) -> Airport | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM airport WHERE code = ?
            """,
            (code, )
        )
        result = cursor.fetchone()
        
        if result is None or len(result) == 0:
            return None
        
        airport = Airport(
            result["id"],
            result["code"],
            result["name"],
            result["city"],
            result["country"],
            result["region"]
        )
        return airport

    def get_airport_list(self) -> list[Airport] | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM airport ORDER BY code
            """
        )
        results = cursor.fetchall()

        if results is None or len(results) == 0:
            return None
        
        result_list = []
        for row in results:
            result_list.append(
                Airport(
                    row["id"],
                    row["code"],
                    row["name"],
                    row["city"],
                    row["country"],
                    row["region"]
                )
            )

        return result_list

    def add_airport(self, airport: Airport) -> None:        
        data = {
            "code": airport.code, 
            "name": airport.name,
            "city": airport.city, 
            "country": airport.country,
            "region": airport.region
        }

        self.conn.execute(
            """
            INSERT INTO airport
                (code, name, city, country, region)
            VALUES
                (:code, :name, :city, :country, :region)
            """,
            data
        )

    def update_airport(self, airport: Airport):
        self.conn.execute(
            """
            UPDATE airport
            SET
                code = ?,
                name = ?,
                city = ?,
                country = ?,
                region = ?
            WHERE id = ?
            """,
            (airport.code, airport.name, airport.city, airport.country, airport.region, airport.id)
        )
    
    def delete_airport(self, airport_id: int):
        self.conn.execute(
            """
            DELETE FROM airport
            WHERE id = ?
            """,
            (airport_id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Airport] | None:
        sql = f"""
            SELECT *
            FROM airport
            WHERE {field_name} = ?
            ORDER BY code
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        if results is None or len(results) == 0:
            return None

        result_list = []
        for row in results:
            result_list.append(
                Airport(
                    row["id"],
                    row["code"],
                    row["name"],
                    row["city"],
                    row["country"],
                    row["region"]
                )
            )

        return result_list
    