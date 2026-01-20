from flightmanagement.models.pilot import Pilot

class PilotRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_by_id(self, pilot_id: int) -> Pilot | None:        
        cursor = self.conn.execute(
            """
            SELECT * FROM pilot WHERE id = ?
            """,
            (pilot_id, )
        )
        result = cursor.fetchone()
        
        if result is None or len(result) == 0:
            return None

        pilot = Pilot(
            id=result["id"],
            first_name=result["first_name"],
            family_name=result["family_name"]
        )
        return pilot

    def get_pilot_list(self) -> list[Pilot] | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM pilot ORDER BY first_name, family_name
            """
        )
        results = cursor.fetchall()
        
        if results is None or len(results) == 0:
            return None
        
        result_list = []
        for row in results:
            result_list.append(
                Pilot(
                    id=row["id"],
                    first_name=row["first_name"],
                    family_name=row["family_name"]
                )
            )

        return result_list

    def add_pilot(self, pilot: Pilot) -> None:        
        data = {
            "first_name": pilot.first_name,
            "family_name": pilot.family_name
        }
        self.conn.execute(
            """
            INSERT INTO pilot
                (first_name, family_name)
            VALUES
                (:first_name, :family_name)
            """,
            data
        )

    def update_pilot(self, pilot: Pilot) -> None:
        self.conn.execute(
            """
            UPDATE pilot
            SET
                first_name = ?,
                family_name = ?
            WHERE id = ?
            """,
            (pilot.first_name, pilot.family_name, pilot.id)
        )
    
    def delete_pilot(self, pilot_id: int) -> None:
        self.conn.execute(
            """
            DELETE FROM pilot
            WHERE id = ?
            """,
            (pilot_id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Pilot] | None:
        sql = f"""
            SELECT *
            FROM pilot
            WHERE {field_name} = ?
            ORDER BY first_name, family_name
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        if results is None or len(results) == 0:
            return None

        result_list = []
        for row in results:
            result_list.append(
                Pilot(
                    id=row["id"],
                    first_name=row["first_name"],
                    family_name=row["family_name"]
                )
            )

        return result_list
    
    
    