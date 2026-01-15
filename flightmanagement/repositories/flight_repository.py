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
            datetime.strptime(result["departure_time_scheduled"], '%Y-%m-%d %H:%M') if result["departure_time_scheduled"] else None,
            datetime.strptime(result["arrival_time_scheduled"], '%Y-%m-%d %H:%M') if result["arrival_time_scheduled"] else None,
            datetime.strptime(result["departure_time_actual"], '%Y-%m-%d %H:%M') if result["departure_time_actual"] else None,
            datetime.strptime(result["arrival_time_actual"], '%Y-%m-%d %H:%M') if result["arrival_time_actual"] else None,
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
                    datetime.strptime(row["departure_time_scheduled"], "%Y-%m-%d %H:%M") if row["departure_time_scheduled"] else None,
                    datetime.strptime(row["arrival_time_scheduled"], "%Y-%m-%d %H:%M") if row["arrival_time_scheduled"] else None,
                    datetime.strptime(row["departure_time_actual"], "%Y-%m-%d %H:%M") if row["departure_time_actual"] else None,
                    datetime.strptime(row["arrival_time_actual"], "%Y-%m-%d %H:%M") if row["arrival_time_actual"] else None,
                    row["status"]
                )
            )

        return result_list

    def get_flight_list(self) -> list[Flight] | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM flight
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
                    datetime.strptime(row["departure_time_scheduled"], "%Y-%m-%d %H:%M") if row["departure_time_scheduled"] else None,
                    datetime.strptime(row["arrival_time_scheduled"], "%Y-%m-%d %H:%M") if row["arrival_time_scheduled"] else None,
                    datetime.strptime(row["departure_time_actual"], "%Y-%m-%d %H:%M") if row["departure_time_actual"] else None,
                    datetime.strptime(row["arrival_time_actual"], "%Y-%m-%d %H:%M") if row["arrival_time_actual"] else None,
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
            "departure_time_scheduled": datetime.strftime(flight.departure_time_scheduled, "%Y-%m-%d %H:%M") if flight.departure_time_scheduled else None,
            "arrival_time_scheduled": datetime.strftime(flight.arrival_time_scheduled, "%Y-%m-%d %H:%M") if flight.arrival_time_scheduled else None,
            "departure_time_actual": datetime.strftime(flight.departure_time_actual, "%Y-%m-%d %H:%M") if flight.departure_time_actual else None,
            "arrival_time_actual": datetime.strftime(flight.arrival_time_actual, "%Y-%m-%d %H:%M") if flight.arrival_time_actual else None,
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
                datetime.strftime(flight.departure_time_scheduled, "%Y-%m-%d %H:%M") if flight.departure_time_scheduled else None,
                datetime.strftime(flight.arrival_time_scheduled, "%Y-%m-%d %H:%M") if flight.arrival_time_scheduled else None,
                datetime.strftime(flight.departure_time_actual, "%Y-%m-%d %H:%M") if flight.departure_time_actual else None,
                datetime.strftime(flight.arrival_time_actual, "%Y-%m-%d %H:%M") if flight.arrival_time_actual else None,
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