from datetime import datetime
from flightmanagement.models.flight import Flight

class FlightRepository:

    def __init__(self, conn):
        self.conn = conn
    
    def get_by_id(self, flight_id: int) -> Flight | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM flight WHERE id = ?
            """,
            (flight_id, )
        )
        result = cursor.fetchone()

        if result is None:
            return None

        flight = Flight(
            result["id"],
            result["flight_number"],
            result["aircraft_id"],
            result["origin_id"],
            result["destination_id"],
            result["pilot_id"],
            result["copilot_id"],
            datetime.strptime(result["departure_time_scheduled"], '%Y-%m-%d %H:%M'),
            datetime.strptime(result["arrival_time_scheduled"], '%Y-%m-%d %H:%M'),
            datetime.strptime(result["departure_time_actual"], '%Y-%m-%d %H:%M') if result[9] else None,
            datetime.strptime(result["arrival_time_actual"], '%Y-%m-%d %H:%M') if result[10] else None,
            result["status"]
        )
        return flight

    def search_on_field(self, field_name: str, value) -> list[Flight] | None:
        sql = f"""
            SELECT *
            FROM flight
            WHERE {field_name} = ?
            ORDER BY departure_time_scheduled DESC
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        if results is None:
            return None

        result_list = []
        for row in results:
            result_list.append(
                Flight(
                    row["id"],
                    row["flight_number"],
                    row["aircraft_id"],
                    row["origin_id"],
                    row["destination_id"],
                    row["pilot_id"],
                    row["copilot_id"],
                    row["departure_time_scheduled"],
                    row["arrival_time_scheduled"],
                    row["departure_time_actual"],
                    row["arrival_time_actual"],
                    row["status"]
                )
            )

        return result_list

    def get_flight_list(self) -> list[Flight] | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM flight ORDER BY departure_time_scheduled DESC
            """
        )
        results = cursor.fetchall()
        
        if results is None:
            return None

        result_list = []
        for row in results:
            result_list.append(
                Flight(
                    row["id"],
                    row["flight_number"],
                    row["aircraft_id"],
                    row["origin_id"],
                    row["destination_id"],
                    row["pilot_id"],
                    row["copilot_id"],
                    row["departure_time_scheduled"],
                    row["arrival_time_scheduled"],
                    row["departure_time_actual"],
                    row["arrival_time_actual"],
                    row["status"]
                )
            )

        return result_list

    def add_flight(self, flight: Flight) -> None:        
        data = {
            "flight_number": flight.flight_number, 
            "aircraft_id": flight.aircraft_id,
            "origin_id": flight.origin_id, 
            "destination_id": flight.destination_id,
            "pilot_id": flight.pilot_id,
            "copilot_id": flight.copilot_id,
            "departure_time_scheduled": flight.departure_time_scheduled,
            "arrival_time_scheduled": flight.arrival_time_scheduled,
            "departure_time_actual": flight.departure_time_actual,
            "arrival_time_actual": flight.arrival_time_actual,
            "status": flight.status
        }
        self.conn.execute(
            """
            INSERT INTO flight
                (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES
                (:flight_number, :aircraft_id, :origin_id, :destination_id, :pilot_id, :copilot_id, :departure_time_scheduled, :arrival_time_scheduled, :departure_time_actual, :arrival_time_actual, :status)
            """,
            data
        )
    
    def update_flight(self, flight: Flight):
        self.conn.execute(
            """
            UPDATE flight
            SET
                flight_number = ?,
                aircraft_id = ?,
                origin_id = ?,
                destination_id = ?,
                pilot_id = ?,
                copilot_id = ?,
                departure_time_scheduled = ?,
                arrival_time_scheduled = ?,
                departure_time_actual = ?,
                arrival_time_actual = ?,
                status = ?
            WHERE id = ?
            """,
            (
                flight.flight_number,
                flight.aircraft_id,
                flight.origin_id,
                flight.destination_id,
                flight.pilot_id,
                flight.copilot_id,
                flight.departure_time_scheduled,
                flight.arrival_time_scheduled,
                flight.departure_time_actual,
                flight.arrival_time_actual,
                flight.status,
                flight.id
            )
        )

    def delete_flight(self, flight_id: int):
        self.conn.execute(
            """
            DELETE FROM flight
            WHERE id = ?
            """,
            (flight_id, )
        )