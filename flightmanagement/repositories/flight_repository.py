from datetime import datetime
from flightmanagement.models.flight import Flight
from flightmanagement.models.pilot import Pilot

class FlightRepository:

    def __init__(self, conn):
        self.conn = conn
    
    def get_item_by_id(self, flight_id: int) -> Flight | None:
        cursor = self.conn.execute(
            """
            SELECT * FROM flight WHERE id = ?
            """,
            (flight_id, )
        )
        result = cursor.fetchone()

        if result is None or len(result) == 0:
            return None

        flight = Flight(
            id=result["id"],
            flight_number=result["flight_number"],
            aircraft_id=result["aircraft_id"],
            origin_id=result["origin_id"],
            destination_id=result["destination_id"],
            pilot_id=result["pilot_id"],
            copilot_id=result["copilot_id"],
            departure_time_scheduled=datetime.strptime(result["departure_time_scheduled"], '%Y-%m-%d %H:%M'),
            arrival_time_scheduled=datetime.strptime(result["arrival_time_scheduled"], '%Y-%m-%d %H:%M'),
            departure_time_actual=datetime.strptime(result["departure_time_actual"], '%Y-%m-%d %H:%M') if result["departure_time_actual"] else None,
            arrival_time_actual=datetime.strptime(result["arrival_time_actual"], '%Y-%m-%d %H:%M') if result["arrival_time_actual"] else None,
            status=result["status"]
        )
        return flight

    def search_on_field(self, field_name: str, value) -> list[Flight]:
        sql = f"""
            SELECT *
            FROM flight
            WHERE {field_name} = ?
            ORDER BY departure_time_scheduled DESC
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(
                Flight(
                    id=row["id"],
                    flight_number=row["flight_number"],
                    aircraft_id=row["aircraft_id"],
                    origin_id=row["origin_id"],
                    destination_id=row["destination_id"],
                    pilot_id=row["pilot_id"],
                    copilot_id=row["copilot_id"],
                    departure_time_scheduled=datetime.strptime(row["departure_time_scheduled"], "%Y-%m-%d %H:%M"),
                    arrival_time_scheduled=datetime.strptime(row["arrival_time_scheduled"], "%Y-%m-%d %H:%M"),
                    departure_time_actual=datetime.strptime(row["departure_time_actual"], "%Y-%m-%d %H:%M") if row["departure_time_actual"] else None,
                    arrival_time_actual=datetime.strptime(row["arrival_time_actual"], "%Y-%m-%d %H:%M") if row["arrival_time_actual"] else None,
                    status=row["status"]
                )
            )

        return result_list

    def get_flight_list(self) -> list[Flight]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM flight
            ORDER BY departure_time_scheduled DESC
            """
        )
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(
                Flight(
                    id=row["id"],
                    flight_number=row["flight_number"],
                    aircraft_id=row["aircraft_id"],
                    origin_id=row["origin_id"],
                    destination_id=row["destination_id"],
                    pilot_id=row["pilot_id"],
                    copilot_id=row["copilot_id"],
                    departure_time_scheduled=datetime.strptime(row["departure_time_scheduled"], "%Y-%m-%d %H:%M"),
                    arrival_time_scheduled=datetime.strptime(row["arrival_time_scheduled"], "%Y-%m-%d %H:%M"),
                    departure_time_actual=datetime.strptime(row["departure_time_actual"], "%Y-%m-%d %H:%M") if row["departure_time_actual"] else None,
                    arrival_time_actual=datetime.strptime(row["arrival_time_actual"], "%Y-%m-%d %H:%M") if row["arrival_time_actual"] else None,
                    status=row["status"]
                )
            )

        return result_list

    def insert_item(self, flight: Flight) -> None:        
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
    
    def update_item(self, flight: Flight):
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

    def delete_item(self, flight: Flight):
        self.conn.execute(
            """
            DELETE FROM flight
            WHERE id = ?
            """,
            (flight.id, )
        )
    
    def get_available_pilots(self, departure_time: datetime, arrival_time: datetime, flight_id: int) -> list[Pilot] | None:
        cursor = self.conn.execute(
            """
            WITH flight_pilot AS (
                SELECT id AS flight_id,
                    pilot_id AS pilot_id,
                    departure_time_scheduled,
                    arrival_time_scheduled,
                    departure_time_actual,
                    arrival_time_actual
                FROM flight
                UNION ALL
                SELECT  id AS flight_id,
                    copilot_id,
                    departure_time_scheduled,
                    arrival_time_scheduled,
                    departure_time_actual,
                    arrival_time_actual
                FROM flight
            ),
            conflicting_flights AS (
                SELECT DISTINCT pilot_id
                FROM flight_pilot
                WHERE
                    (
                        (departure_time_scheduled <= ? AND arrival_time_scheduled >= ?)
                        OR (departure_time_scheduled <= ? AND arrival_time_scheduled >= ?)
                    ) AND flight_id <> ?
            ),
            flight_hours AS (
                SELECT
                    pilot_id,
                    ROUND(SUM(
                        (UNIXEPOCH(IFNULL(arrival_time_actual, arrival_time_scheduled))
                    - UNIXEPOCH(IFNULL(departure_time_actual, departure_time_scheduled))
                    ) / 3600.0), 2) AS hours
                FROM flight_pilot
                WHERE arrival_time_scheduled IS NOT NULL
                AND departure_time_scheduled IS NOT NULL
                AND arrival_time_scheduled > datetime(?, '-28 days')
                GROUP BY pilot_id
            )
            SELECT p.*
            FROM pilot p
            LEFT JOIN conflicting_flights c ON c.pilot_id = p.id
            LEFT JOIN flight_hours h ON h.pilot_id = p.id
            WHERE c.pilot_id IS NULL
            AND IFNULL(h.hours, 0.0)
                < (100 - ((unixepoch(?)
                        - unixepoch(?)) / 3600.0))
            """,
            (
                departure_time,
                departure_time,
                arrival_time,
                arrival_time,
                flight_id,
                departure_time,
                arrival_time,
                departure_time
            )
        )
        results = cursor.fetchall()

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