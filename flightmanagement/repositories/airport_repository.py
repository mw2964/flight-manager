from flightmanagement.models.airport import Airport

class AirportRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_item_by_id(self, airport_id: int) -> Airport | None:        
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
            id=result["id"],
            code=result["code"],
            name=result["name"],
            city=result["city"],
            country=result["country"],
            region=result["region"]
        )
        return airport

    def get_item_by_code(self, code: str) -> Airport | None:
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
            id=result["id"],
            code=result["code"],
            name=result["name"],
            city=result["city"],
            country=result["country"],
            region=result["region"]
        )
        return airport

    def get_airport_list(self) -> list[Airport]:
        cursor = self.conn.execute(
            """
            SELECT * FROM airport ORDER BY code
            """
        )
        results = cursor.fetchall()

        result_list = []
        for row in results:
            result_list.append(
                Airport(
                    id=row["id"],
                    code=row["code"],
                    name=row["name"],
                    city=row["city"],
                    country=row["country"],
                    region=row["region"]
                )
            )

        return result_list

    def insert_item(self, airport: Airport) -> None:        
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

    def update_item(self, airport: Airport):
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
    
    def delete_item(self, airport: Airport):
        self.conn.execute(
            """
            DELETE FROM airport
            WHERE id = ?
            """,
            (airport.id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Airport]:
        sql = f"""
            SELECT *
            FROM airport
            WHERE {field_name} = ?
            ORDER BY code
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(
                Airport(
                    id=row["id"],
                    code=row["code"],
                    name=row["name"],
                    city=row["city"],
                    country=row["country"],
                    region=row["region"]
                )
            )

        return result_list
    