from flightmanagement.models.pilot import Pilot
from datetime import date

class PilotRepository:

    def __init__(self, conn):
        self.conn = conn

    # Core pilot functionality

    def get_pilot_by_id(self, staff_id: int) -> Pilot | None:        
        cursor = self.conn.execute(
            """
            SELECT *
            FROM vw_staff_pilots
            WHERE staff_id = ?
            """,
            (staff_id, )
        )
        result = cursor.fetchone()        
        return self.dict_to_pilot(result)

    def get_pilot_list(self) -> list[Pilot]:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM vw_staff_pilots
            ORDER BY first_name, family_name
            """
        )
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(self.dict_to_pilot(row))

        return result_list

    def insert_pilot(self, pilot: Pilot) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO staff
                (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                (:employee_number, :first_name, :family_name, :employment_status, :employment_start_date, :employment_end_date)
            """,
            pilot.to_dict_staff
        )        
        new_id = cur.lastrowid()

        self.conn.execute(
            """
            INSERT INTO pilots
                (staff_id, license_number, license_type, license_expiration_date)
            VALUES
                (:staff_id, :license_number, :license_type, :license_expiration_date)
            """,
            pilot.to_dict_pilot(new_id)
        )

    def update_pilot(self, pilot: Pilot) -> None:
        self.conn.execute(
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
                pilot.employment_start_date,
                pilot.employment_end_date,
                pilot.staff_id
            )
        )

        self.conn.execute(
            """
            UPDATE pilot
            SET
                license_number = ?,
                license_type = ?,
                license_expiration_date = ?
            WHERE staff_id = ?
            """,
            (
                pilot.license_number,
                pilot.license_type,
                pilot.license_expiration_date,
                pilot.staff_id
            )
        )
    
    def delete_staff(self, pilot: Pilot) -> None:
        self.conn.execute(
            """
            DELETE FROM staff
            WHERE staff_id = ?
            """,
            (pilot.staff_id, )
        )

    def delete_pilot(self, pilot: Pilot) -> None:
        self.conn.execute(
            """
            DELETE FROM pilot
            WHERE staff_id = ?
            """,
            (pilot.staff_id, )
        )
    
    def search_on_field(self, field_name: str, value) -> list[Pilot]:
        sql = f"""
            SELECT *
            FROM vw_staff_pilots
            WHERE {field_name} = ?
            ORDER BY first_name, family_name
        """
        cursor = self.conn.execute(sql, (value, ))
        results = cursor.fetchall()
        
        result_list = []
        for row in results:
            result_list.append(self.dict_to_pilot(row))

        return result_list
    
    def dict_to_pilot(self, data: dict | None) -> Pilot | None:
        if data is None or len(data) == 0:
            return None

        return Pilot(
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
    
    # Leave booking functionality

    def get_leave_bookings_by_staff_id(self, staff_id: int) -> list:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM leave_bookings
            WHERE staff_id = ?
            """,
            (staff_id, )
        )
        result_list = cursor.fetchall()
        return result_list
    
    def insert_leave_booking(self, staff_id: int, leave_date: date, leave_type: str | None = None):
        self.conn.execute(
            """
            INSERT INTO leave_bookings
                (staff_id, leave_date, leave_type)
            VALUES
                (:staff_id, :leave_date, :leave_type) 
            """,
            {
                "staff_id": staff_id,
                "leave_date": leave_date,
                "leave_type": leave_type
            }
        )

    def delete_leave_booking(self, staff_id: int, leave_date: date):
        self.conn.execute(
            """
            DELETE FROM leave_bookings
            WHERE staff_id = ?
            AND leave_date = ?
            """,
            (staff_id, leave_date)
        )

    def update_leave_booking(self, staff_id: int, old_leave_date: date, new_leave_date: date, leave_type: str | None = None):
        self.delete_leave_booking(staff_id, old_leave_date)
        self.insert_leave_booking(staff_id, new_leave_date, leave_type)
    
    # Flight hours logging functionality

    def get_flight_logs_by_staff_id(self, staff_id: int) -> list:
        cursor = self.conn.execute(
            """
            SELECT *
            FROM flight_time_logs
            WHERE staff_id = ?
            """,
            (staff_id, )
        )
        result_list = cursor.fetchall()
        return result_list
    
    def insert_flight_log_record(self, staff_id: int, effective_date: date, flight_hours: float):
        self.conn.execute(
            """
            INSERT INTO flight_time_hours
                (staff_id, effective_date, flight_hours)
            VALUES
                (:staff_id, :effective_date, :flight_hours) 
            """,
            {
                "staff_id": staff_id,
                "effective_date": effective_date,
                "flight_hours": flight_hours
            }
        )

    def delete_flight_log_record(self, staff_id: int, effective_date: date):
        self.conn.execute(
            """
            DELETE FROM flight_time_hours
            WHERE staff_id = ?
            AND effective_date = ?
            """,
            (staff_id, effective_date)
        )

    def update_flight_log_record(self, staff_id: int, effective_date: date, flight_hours: float):
        self.conn.execute(
            """
            UPDATE flight_time_hours
            SET flight_hours = ?
            WHERE staff_id = ?
            AND effective_date = ?
            """,
            (flight_hours, staff_id, effective_date)
        )