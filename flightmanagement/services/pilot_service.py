from datetime import date
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.pilot import Pilot
from flightmanagement.db.db import transaction

class PilotService:

    def __init__(self, conn, pilot_repository=None):
        self.conn = conn
        self.__pilot_repository = (
            pilot_repository or PilotRepository(self.conn)
        )

    def add_pilot(self, pilot: Pilot):
        with transaction(self.conn):
            self.__pilot_repository.insert_pilot(pilot)

    def update_pilot(self, pilot: Pilot):
        with transaction(self.conn):
            self.__pilot_repository.update_pilot(pilot)

    def delete_pilot(self, pilot: Pilot):
        if pilot.staff_id is None:
            raise ValueError("Pilot to delete lacks an ID")
        with transaction(self.conn):
            self.__pilot_repository.delete_pilot(pilot)

    def add_time_log_record(self, staff_id: int, effective_date: date, flight_hours: float):
        with transaction(self.conn):
            self.__pilot_repository.insert_flight_log_record(
                staff_id = staff_id,
                effective_date = effective_date,
                flight_hours = flight_hours
            )

    def update_time_log_record(self, staff_id: int, effective_date: date, flight_hours: float):
        with transaction(self.conn):
            self.__pilot_repository.update_flight_log_record(
                staff_id = staff_id,
                effective_date = effective_date,
                flight_hours = flight_hours
            )

    def delete_time_log_record(self, staff_id: int, effective_date: date):
        with transaction(self.conn):
            self.__pilot_repository.delete_flight_log_record(
                staff_id = staff_id,
                effective_date = effective_date
            )

    def add_leave_booking_record(self, staff_id: int, leave_date: date, leave_type: str):
        with transaction(self.conn):
            self.__pilot_repository.insert_leave_booking(
                staff_id = staff_id,
                leave_date = leave_date,
                leave_type = leave_type
            )

    def update_leave_booking_record(self, staff_id: int, leave_date: date, leave_type: str):
        with transaction(self.conn):
            self.__pilot_repository.update_leave_booking(
                staff_id = staff_id,
                leave_date = leave_date,
                leave_type = leave_type
            )

    def delete_leave_booking_record(self, staff_id: int, leave_date: date):
        with transaction(self.conn):
            self.__pilot_repository.delete_leave_booking(
                staff_id = staff_id,
                leave_date = leave_date
            )

    def log_record_exists(self, staff_id: int, effective_date: date) -> bool:
        if self.__pilot_repository.get_flight_log_record_by_staff_id_and_date(staff_id, effective_date):
            return True
        return False

    def leave_record_exists(self, staff_id: int, leave_date: date) -> bool:
        if self.__pilot_repository.get_leave_record_by_staff_id_and_date(staff_id, leave_date):
            return True
        return False

    def get_pilot_table(self) -> str:
        pilots = self.__pilot_repository.get_pilot_list()

        if pilots is None:
            return ""
        
        return self.get_results_view(pilots)
    
    def get_flight_logs_table(self, staff_id: int) -> str:
        records = self.__pilot_repository.get_flight_logs_by_staff_id(staff_id)

        if records is None:
            return ""
        
        return self.get_log_results_view(records)

    def get_leave_bookings_table(self, staff_id: int) -> str:
        records = self.__pilot_repository.get_leave_bookings_by_staff_id(staff_id)

        if records is None:
            return ""
        
        return self.get_leave_results_view(records)

    def get_pilot_choices(self) -> list:
        pilots = self.__pilot_repository.get_pilot_list()
        
        pilot_choices = []

        if pilots:
            for pilot in pilots:
                pilot_choices.append((pilot["staff_id"], f"{pilot['family_name']}, {pilot['first_name']}"))

        return pilot_choices

    def get_leave_record_choices(self, staff_id: int) -> list:
        records = self.__pilot_repository.get_leave_bookings_by_staff_id(staff_id)
        
        record_choices = []
        if records:
            for record in records:
                record_choices.append((record["leave_date"], f"{record['leave_date']} ({record['leave_type']})"))

        return record_choices

    def get_time_log_record(self, staff_id: int, effective_date: date) -> dict | None:
        log_record = self.__pilot_repository.get_flight_log_record_by_staff_id_and_date(staff_id, effective_date)
        if log_record:
            return {
                "staff_id": log_record[0],
                "effective_date": date.fromisoformat(log_record[1]),
                "flight_hours": float(log_record[2])
            }
        return None

    def get_leave_booking_record(self, staff_id: int, leave_date: date) -> dict | None:
        leave_record = self.__pilot_repository.get_leave_record_by_staff_id_and_date(staff_id, leave_date)
        if leave_record:
            return {
                "staff_id": leave_record[0],
                "leave_date": date.fromisoformat(leave_record[1]),
                "leave_type": leave_record[2]
            }
        return None

    def get_log_record_choices(self, staff_id: int) -> list:
        records = self.__pilot_repository.get_flight_logs_by_staff_id(staff_id)
        
        record_choices = []
        if records:
            for record in records:
                record_choices.append((record["effective_date"], f"{record['effective_date']}: {record['flight_hours']} hrs"))

        return record_choices

    def search_pilots(self, field_name: str, value) -> list[Pilot]:
        return self.__pilot_repository.search_on_field(field_name, value)

    def get_pilot_by_id(self, id: int):
        return self.__pilot_repository.get_pilot_by_id(id)
    
    def get_results_view(self, pilots: list) -> str:
        if pilots is None or len(pilots) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Staff ID",
            "Family name",
            "First name",
            "Employee number",
            "Status",            
            "Date started",
            "Date left",
            "License number",
            "License type",
            "License expiry"
        ])

        # Populate table rows
        for pilot in pilots:
            table.add_row([
                pilot["staff_id"],
                pilot["family_name"],
                pilot["first_name"],
                pilot["employee_number"],
                pilot["employment_status"],
                pilot["employment_start_date"],
                pilot["employment_end_date"],
                pilot["license_number"],
                pilot["license_type"],
                pilot["license_expiration_date"]
            ])

        # Set table formatting
        table.set_style(TableStyle.SINGLE_BORDER)
        table.align = "l"
        table.max_width = 20
        table.hrules = ALL
        table.vrules = NONE
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"

        return str(indented_table)
    
    def get_log_results_view(self, logs: list) -> str:
        if logs is None or len(logs) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Effective date",
            "Flight hours"
        ])

        # Populate table rows
        for record in logs:
            table.add_row([
                record["effective_date"],
                record["flight_hours"]
            ])

        # Set table formatting
        table.set_style(TableStyle.SINGLE_BORDER)
        table.align = "l"
        table.max_width = 20
        table.hrules = ALL
        table.vrules = NONE
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"

        return str(indented_table)
    
    def get_leave_results_view(self, logs: list) -> str:
        if logs is None or len(logs) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Leave date",
            "Leave type"
        ])

        # Populate table rows
        for record in logs:
            table.add_row([
                record["leave_date"],
                record["leave_type"]
            ])

        # Set table formatting
        table.set_style(TableStyle.SINGLE_BORDER)
        table.align = "l"
        table.max_width = 20
        table.hrules = ALL
        table.vrules = NONE
    
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"

        return str(indented_table)

    def display_record(self, pilot: Pilot) -> str:
        return f"\n> Pilot ID: {pilot.staff_id}\n> First name: {pilot.first_name}\n> Family name: {pilot.family_name}"