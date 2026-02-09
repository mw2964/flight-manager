from datetime import datetime, date, time
from flightmanagement.models.flight import Flight
from flightmanagement.models.pilot import Pilot
from flightmanagement.repositories.base_repository import BaseRepository

class FlightRepository(BaseRepository):

    def __init__(self, conn):
        super().__init__(conn)
    
    def get_flight_by_id(self, flight_id: int) -> Flight | None:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM flights
            WHERE flight_id = ?
            """,
            (flight_id, )
        )
        return self.dict_to_flight(row)
    
    def get_flight_summary_by_id(self, flight_id: int) -> dict:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM vw_flight_summary
            WHERE flight_id = ?
            """,
            (flight_id, )
        )
        return dict(row)

    def search_on_field(self, field_name: str, value) -> list[dict]:
        sql = f"""
            SELECT *
            FROM vw_flight_summary
            WHERE {field_name} = ?
            ORDER BY scheduled_departure_date DESC
        """
        rows = self._execute_fetchall(sql, (value, ))
        
        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list

    def get_flight_list(self) -> list[Flight]:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM flights
            ORDER BY scheduled_departure_date DESC, scheduled_departure_time DESC
            """
        )
        
        result_list = []
        for row in rows:
            result_list.append(self.dict_to_flight(row))

        return result_list

    def get_flight_summary_list(self) -> list[dict]:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM vw_flight_summary
            ORDER BY scheduled_departure_date DESC
            """
        )

        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list

    def get_relief_pilots_by_flight_id(self, flight_id: int) -> list[int]:
        rows = self._execute_fetchall(
            """
            SELECT staff_member_id
            FROM flight_relief_pilots
            WHERE flight_id = ?
            """,
            (flight_id, )
        )

        result_list = []
        for row in rows:
            result_list.append(row["staff_member_id"])

        return result_list

    def insert_flight(self, flight: Flight) -> int:
        row = self._execute_fetchone(
            """
            INSERT INTO flights (                
                aircraft_id,
                origin_location_id,
                destination_location_id,
                departure_gate_id,
                arrival_gate_id,
                captain_id,
                first_officer_id,
                flight_number,
                scheduled_departure_date,
                scheduled_departure_time,
                scheduled_arrival_date,
                scheduled_arrival_time,
                confirmed_departure_date,
                confirmed_departure_time,
                confirmed_arrival_date,
                confirmed_arrival_time,
                flight_status
            )
            VALUES (
                :aircraft_id,
                :origin_location_id,
                :destination_location_id,
                :departure_gate_id,
                :arrival_gate_id,
                :captain_id,
                :first_officer_id,
                :flight_number,
                :scheduled_departure_date,
                :scheduled_departure_time,
                :scheduled_arrival_date,
                :scheduled_arrival_time,
                :confirmed_departure_date,
                :confirmed_departure_time,
                :confirmed_arrival_date,
                :confirmed_arrival_time,
                :flight_status
            )
            RETURNING flight_id
            """,
            {
                "aircraft_id": flight.aircraft_id,
                "origin_location_id": flight.origin_location_id, 
                "destination_location_id": flight.destination_location_id,
                "departure_gate_id": flight.departure_gate_id,
                "arrival_gate_id": flight.arrival_gate_id,
                "captain_id": flight.captain_id,
                "first_officer_id": flight.first_officer_id,
                "flight_number": flight.flight_number,
                "scheduled_departure_date": flight.scheduled_departure_date.strftime("%Y-%m-%d"),
                "scheduled_departure_time": flight.scheduled_departure_time.strftime("%H:%M"),
                "scheduled_arrival_date": flight.scheduled_arrival_date.strftime("%Y-%m-%d"),
                "scheduled_arrival_time": flight.scheduled_arrival_time.strftime("%H:%M"),
                "confirmed_departure_date": flight.confirmed_departure_date.strftime("%Y-%m-%d") if flight.confirmed_departure_date else None,
                "confirmed_departure_time": flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None,
                "confirmed_arrival_date": flight.confirmed_arrival_date.strftime("%Y-%m-%d") if flight.confirmed_arrival_date else None,
                "confirmed_arrival_time": flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None,
                "flight_status": flight.flight_status
            }
        )
        return row["flight_id"]

    def update_flight(self, flight: Flight):
        self._execute(
            """
            UPDATE flights
            SET
                aircraft_id = ?,
                origin_location_id = ?,
                destination_location_id = ?,
                departure_gate_id = ?,
                arrival_gate_id = ?,
                captain_id = ?,
                first_officer_id = ?,
                flight_number = ?,
                scheduled_departure_date = ?,
                scheduled_departure_time = ?,
                scheduled_arrival_date = ?,
                scheduled_arrival_time = ?,
                confirmed_departure_date = ?,
                confirmed_departure_time = ?,
                confirmed_arrival_date = ?,
                confirmed_arrival_time = ?,
                flight_status = ?
            WHERE flight_id = ?
            """,
            (                
                flight.aircraft_id,
                flight.origin_location_id,
                flight.destination_location_id,
                flight.departure_gate_id,
                flight.arrival_gate_id,
                flight.captain_id,
                flight.first_officer_id,
                flight.flight_number,
                flight.scheduled_departure_date.strftime("%Y-%m-%d") if flight.scheduled_departure_date else None,
                flight.scheduled_departure_time.strftime("%H:%M") if flight.scheduled_departure_time else None,
                flight.scheduled_arrival_date.strftime("%Y-%m-%d") if flight.scheduled_arrival_date else None,
                flight.scheduled_arrival_time.strftime("%H:%M") if flight.scheduled_arrival_time else None,
                flight.confirmed_departure_date.strftime("%Y-%m-%d") if flight.confirmed_departure_date else None,
                flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None,
                flight.confirmed_arrival_date.strftime("%Y-%m-%d") if flight.confirmed_arrival_date else None,
                flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None,
                flight.flight_status,
                flight.flight_id
            )
        )

    def delete_flight(self, flight: Flight):
        self._execute(
            """
            DELETE FROM flights
            WHERE flight_id = ?
            """,
            (flight.flight_id, )
        )
    
    def insert_relief_pilot(self, flight: Flight, staff_member_id: int):
        self._execute(
            """
            INSERT INTO flight_relief_pilots (
                flight_id,
                staff_member_id
            )
            VALUES (
                :flight_id,
                :staff_member_id
            )
            """,
            {
                "flight_id": flight.flight_id,
                "staff_member_id": staff_member_id
            }
        )

    def delete_relief_pilot(self, flight: Flight, staff_member_id: int):
        self._execute(
            """
            DELETE FROM flight_relief_pilots
            WHERE flight_id = ?
            AND staff_member_id = ?
            """,
            (flight.flight_id, staff_member_id)
        )

    def dict_to_flight(self, data: dict | None) -> Flight | None:
        if data is None or len(data) == 0:
            return None

        return Flight(
            flight_id = data["flight_id"],
            aircraft_id = data["aircraft_id"],
            origin_location_id = data["origin_location_id"], 
            destination_location_id = data["destination_location_id"],
            departure_gate_id = data["departure_gate_id"],
            arrival_gate_id = data["arrival_gate_id"],
            captain_id = data["captain_id"],
            first_officer_id = data["first_officer_id"],
            flight_number = data["flight_number"],
            scheduled_departure_date = date.fromisoformat(data["scheduled_departure_date"]),
            scheduled_departure_time = time.fromisoformat(data["scheduled_departure_time"]),
            scheduled_arrival_date = date.fromisoformat(data["scheduled_arrival_date"]),
            scheduled_arrival_time = time.fromisoformat(data["scheduled_arrival_time"]),
            confirmed_departure_date = date.fromisoformat(data["confirmed_departure_date"]) if data["confirmed_departure_date"] else None,
            confirmed_departure_time = time.fromisoformat(data["confirmed_departure_time"]) if data["confirmed_departure_time"] else None,
            confirmed_arrival_date = date.fromisoformat(data["confirmed_arrival_date"]) if data["confirmed_arrival_date"] else None,
            confirmed_arrival_time = time.fromisoformat(data["confirmed_arrival_time"]) if data["confirmed_arrival_time"] else None,
            flight_status = data["flight_status"]
        )
    
    def dict_to_pilot(self, data: dict | None) -> Pilot | None:
        if data is None or len(data) == 0:
            return None

        return Pilot(
            staff_member_id = data["staff_member_id"],
            employee_number = data["employee_number"],
            first_name = data["first_name"],
            family_name = data["family_name"],
            employment_start_date = data["employment_start_date"],
            employment_status = data["employment_status"],
            employment_end_date = data["employment_end_date"],
            license_number = data["license_number"],
            license_type = data["license_type"],
            license_expiration_date = data["license_expiration_date"]
        )