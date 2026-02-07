from flightmanagement.repositories.base_repository import BaseRepository
from flightmanagement.models.pilot import Pilot
from datetime import date, datetime

class PilotRepository(BaseRepository):

    PILOT_SEARCH_FIELDS = {
        'first_name',
        'family_name',
        'employee_number',
        'employment_status',
        'employment_start_date',
        'employment_end_date',
        'license_number',
        'license_type',
        'license_expiration_date'
    }

    def __init__(self, conn):
        super().__init__(conn)

    # Core pilot functionality

    def get_pilot_by_id(self, staff_id: int) -> Pilot | None:        
        row = self._execute_fetchone(
            """
            SELECT *
            FROM vw_staff_pilots
            WHERE staff_id = ?
            """,
            (staff_id, )
        )     
        return self.dict_to_pilot(row)

    def get_pilot_list(self) -> list:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM vw_staff_pilots
            ORDER BY family_name, first_name
            """
        )

        result_list = []
        for row in rows:
            result_list.append(self.dict_to_pilot(row))

        return result_list

        return rows

    def search_on_field(self, field_name: str, value) -> list:
        if field_name not in self.PILOT_SEARCH_FIELDS:
            raise ValueError(f"Invalid search field: {field_name}")

        sql = f"""
            SELECT *
            FROM vw_staff_pilots
            WHERE {field_name} = ?
            ORDER BY family_name, first_name
        """
        rows = self._execute_fetchall(sql, (value, ))
        
        result_list = []
        for row in rows:
            result_list.append(self.dict_to_pilot(row))

        return result_list

    def insert_pilot(self, pilot: Pilot) -> int:
        row = self._execute_fetchone(
            """
            INSERT INTO staff
                (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                (:employee_number, :first_name, :family_name, :employment_status, :employment_start_date, :employment_end_date)
            RETURNING staff_id
            """,
            {
                "employee_number": pilot.employee_number,
                "first_name": pilot.first_name, 
                "family_name": pilot.family_name,
                "employment_status": pilot.employment_status,
                "employment_start_date": pilot.employment_start_date.strftime("%Y-%m-%d"),
                "employment_end_date": pilot.employment_end_date.strftime("%Y-%m-%d") if pilot.employment_end_date else None
            }
        )

        self._execute(
            """
            INSERT INTO pilots
                (staff_id, license_number, license_type, license_expiration_date)
            VALUES
                (:staff_id, :license_number, :license_type, :license_expiration_date)
            """,
            {
                "staff_id": row["staff_id"],
                "license_number": pilot.license_number,
                "license_type": pilot.license_type,
                "license_expiration_date": pilot.license_expiration_date.strftime("%Y-%m-%d") if pilot.license_expiration_date else None
            }
        )
        return row["staff_id"]

    def update_pilot(self, pilot: Pilot) -> None:
        self._execute(
            """
            UPDATE staff
            SET
                employee_number = ?,
                first_name = ?,
                family_name = ?,
                employment_status = ?,
                employment_start_date = ?,
                employment_end_date = ?
            WHERE staff_id = ?
            """,
            (
                pilot.employee_number,
                pilot.first_name,
                pilot.family_name,
                pilot.employment_status,
                pilot.employment_start_date.strftime("%Y-%m-%d"),
                pilot.employment_end_date.strftime("%Y-%m-%d") if pilot.employment_end_date else None,
                pilot.staff_id
            )
        )
        
        self._execute(
            """
            UPDATE pilots
            SET
                license_number = ?,
                license_type = ?,
                license_expiration_date = ?
            WHERE staff_id = ?
            """,
            (
                pilot.license_number,
                pilot.license_type,
                pilot.license_expiration_date.strftime("%Y-%m-%d") if pilot.license_expiration_date else None,
                pilot.staff_id
            )
        )

    def delete_pilot(self, pilot: Pilot) -> None:
        self._execute(
            """
            DELETE FROM pilots
            WHERE staff_id = ?
            """,
            (pilot.staff_id, )
        )

    def delete_staff(self, pilot: Pilot) -> None:
        self._execute(
            """
            DELETE FROM staff
            WHERE staff_id = ?
            """,
            (pilot.staff_id, )
        )
    
    def dict_to_pilot(self, data: dict | None) -> Pilot | None:
        if data is None or len(data) == 0:
            return None

        return Pilot(
            staff_id = data["staff_id"],
            employee_number = data["employee_number"],
            first_name = data["first_name"],
            family_name = data["family_name"],
            employment_start_date = date.fromisoformat(data["employment_start_date"]),
            employment_status = data["employment_status"],
            employment_end_date = date.fromisoformat(data["employment_end_date"]) if data["employment_end_date"] is not None else None,
            license_number = data["license_number"],
            license_type = data["license_type"],
            license_expiration_date = date.fromisoformat(data["license_expiration_date"]) if data["license_expiration_date"] is not None else None
        )
    
    # Leave booking functionality

    def get_leave_bookings_by_staff_id(self, staff_id: int) -> list:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM leave_bookings
            WHERE staff_id = ?
            """,
            (staff_id, )
        )
        return rows

    def get_leave_record_by_staff_id_and_date(self, staff_id: int, leave_date: date) -> list:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM leave_bookings
            WHERE staff_id = ?
            AND leave_date = ?
            """,
            (staff_id, leave_date.strftime("%Y-%m-%d"))
        )
        result = cursor.fetchone()
        return result

    def insert_leave_booking(self, staff_id: int, leave_date: date, leave_type: str | None = None):
        self._execute(
            """
            INSERT INTO leave_bookings
                (staff_id, leave_date, leave_type)
            VALUES
                (:staff_id, :leave_date, :leave_type) 
            """,
            {
                "staff_id": staff_id,
                "leave_date": leave_date.strftime("%Y-%m-%d"),
                "leave_type": leave_type
            }
        )

    def delete_leave_booking(self, staff_id: int, leave_date: date):
        self._execute(
            """
            DELETE FROM leave_bookings
            WHERE staff_id = ?
            AND leave_date = ?
            """,
            (staff_id, leave_date)
        )

    def update_leave_booking(self, staff_id: int, leave_date: date, leave_type: str):
        self._execute(
            """
            UPDATE leave_bookings
            SET leave_type = ?
            WHERE staff_id = ?
            AND leave_date = ?
            """,
            (leave_type, staff_id, leave_date.strftime("%Y-%m-%d"))
        )
    
    # Flight hours logging functionality

    def get_flight_logs_by_staff_id(self, staff_id: int) -> list:
        rows = self._execute_fetchall(
            """
            SELECT *
            FROM flight_time_logs
            WHERE staff_id = ?
            """,
            (staff_id, )
        )
        return rows
    
    def get_flight_log_record_by_staff_id_and_date(self, staff_id: int, effective_date: date) -> list:
        row = self._execute_fetchone(
            """
            SELECT *
            FROM flight_time_logs
            WHERE staff_id = ?
            AND effective_date = ?
            """,
            (staff_id, effective_date.strftime("%Y-%m-%d"))
        )
        return row

    def insert_flight_log_record(self, staff_id: int, effective_date: date, flight_hours: float):
        self._execute(
            """
            INSERT INTO flight_time_logs
                (staff_id, effective_date, flight_hours)
            VALUES
                (:staff_id, :effective_date, :flight_hours) 
            """,
            {
                "staff_id": staff_id,
                "effective_date": effective_date.strftime("%Y-%m-%d"),
                "flight_hours": flight_hours
            }
        )

    def delete_flight_log_record(self, staff_id: int, effective_date: date):
        self._execute(
            """
            DELETE FROM flight_time_logs
            WHERE staff_id = ?
            AND effective_date = ?
            """,
            (staff_id, effective_date.strftime("%Y-%m-%d"))
        )

    def update_flight_log_record(self, staff_id: int, effective_date: date, flight_hours: float):
        self._execute(
            """
            UPDATE flight_time_logs
            SET flight_hours = ?
            WHERE staff_id = ?
            AND effective_date = ?
            """,
            (flight_hours, staff_id, effective_date.strftime("%Y-%m-%d"))
        )