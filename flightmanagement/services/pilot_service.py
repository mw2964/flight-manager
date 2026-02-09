from datetime import date, datetime
from prettytable import PrettyTable
from flightmanagement.error import MissingData, DependentRecords, DuplicateRecord, InvalidData, ForeignKeyDependencyViolation, ForeignKeyInvalidViolation, UniqueConstraintViolation, CheckConstraintViolation, MissingNotNullViolation
from flightmanagement.services.service_utils import format_table
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.models.pilot import Pilot
from flightmanagement.db.db import transaction

class PilotService:

    def __init__(self, conn, pilot_repository = None):
        self.conn = conn
        self.__pilot_repository = (
            pilot_repository or PilotRepository(self.conn)
        )

    def add_pilot(self, pilot: Pilot) -> int:
        try:
            with transaction(self.conn):
                return self.__pilot_repository.insert_pilot(pilot)
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def update_pilot(self, pilot: Pilot):
        try:
            with transaction(self.conn):
                self.__pilot_repository.update_pilot(pilot)
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def delete_pilot(self, pilot: Pilot):
        if pilot.staff_member_id is None:
            raise ValueError("Pilot to delete lacks an ID")
        
        try:
            with transaction(self.conn):
                self.__pilot_repository.delete_pilot(pilot)
                self.__pilot_repository.delete_staff_member(pilot)
        except ForeignKeyDependencyViolation as e:
            raise DependentRecords(e)

    def add_time_log_record(self, staff_member_id: int, effective_date: date, flight_hours: float):
        try:
            with transaction(self.conn):
                self.__pilot_repository.insert_flight_log_record(
                    staff_member_id = staff_member_id,
                    effective_date = effective_date,
                    flight_hours = flight_hours
                )
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def update_time_log_record(self, staff_member_id: int, effective_date: date, flight_hours: float):
        try:
            with transaction(self.conn):
                self.__pilot_repository.update_flight_log_record(
                    staff_member_id = staff_member_id,
                    effective_date = effective_date,
                    flight_hours = flight_hours
                )
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def delete_time_log_record(self, staff_member_id: int, effective_date: date):
        with transaction(self.conn):
            self.__pilot_repository.delete_flight_log_record(
                staff_member_id = staff_member_id,
                effective_date = effective_date
            )

    def add_leave_booking_record(self, staff_member_id: int, leave_date: date, leave_type: str):
        try:
            with transaction(self.conn):
                self.__pilot_repository.insert_leave_booking(
                    staff_member_id = staff_member_id,
                    leave_date = leave_date,
                    leave_type = leave_type
                )
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def update_leave_booking_record(self, staff_member_id: int, leave_date: date, leave_type: str):
        try:
            with transaction(self.conn):
                self.__pilot_repository.update_leave_booking(
                    staff_member_id = staff_member_id,
                    leave_date = leave_date,
                    leave_type = leave_type
                )
        except (ForeignKeyDependencyViolation, ForeignKeyInvalidViolation) as e:
            raise DependentRecords(e)
        except UniqueConstraintViolation as e:
            raise DuplicateRecord(e)
        except CheckConstraintViolation as e:
            raise InvalidData(e)
        except MissingNotNullViolation as e:
            raise MissingData(e)

    def delete_leave_booking_record(self, staff_member_id: int, leave_date: date):
        with transaction(self.conn):
            self.__pilot_repository.delete_leave_booking(
                staff_member_id = staff_member_id,
                leave_date = leave_date
            )

    def log_record_exists(self, staff_member_id: int, effective_date: date) -> bool:
        if self.__pilot_repository.get_flight_log_record_by_staff_member_id_and_date(staff_member_id, effective_date):
            return True
        return False

    def leave_record_exists(self, staff_member_id: int, leave_date: date) -> bool:
        if self.__pilot_repository.get_leave_record_by_staff_member_id_and_date(staff_member_id, leave_date):
            return True
        return False

    def get_pilot_table(self) -> str:
        pilots = self.__pilot_repository.get_pilot_list()

        if pilots is None:
            return ""
        
        return self.get_results_view(pilots)
    
    def get_flight_logs_table(self, staff_member_id: int) -> str:
        records = self.__pilot_repository.get_flight_logs_by_staff_member_id(staff_member_id)

        if records is None:
            return ""
        
        return self.get_log_results_view(records)

    def get_leave_bookings_table(self, staff_member_id: int) -> str:
        records = self.__pilot_repository.get_leave_bookings_by_staff_member_id(staff_member_id)

        if records is None:
            return ""
        
        return self.get_leave_results_view(records)

    def get_pilot_choices(self) -> list:
        pilots = self.__pilot_repository.get_pilot_list()
        
        pilot_choices = []

        if pilots:
            for pilot in pilots:
                pilot_choices.append((pilot.staff_member_id, f"{pilot.family_name}, {pilot.first_name}"))

        return pilot_choices

    def get_leave_record_choices(self, staff_member_id: int) -> list:
        records = self.__pilot_repository.get_leave_bookings_by_staff_member_id(staff_member_id)
        
        record_choices = []
        if records:
            for record in records:
                leave_date = datetime.strptime(record["leave_date"], "%Y-%m-%d").strftime("%d/%m/%Y")
                record_choices.append((leave_date, f"{leave_date} ({record['leave_type']})"))

        return record_choices

    def get_time_log_record(self, staff_member_id: int, effective_date: date) -> dict | None:
        log_record = self.__pilot_repository.get_flight_log_record_by_staff_member_id_and_date(staff_member_id, effective_date)
        if log_record:
            return {
                "staff_member_id": log_record[0],
                "effective_date": date.fromisoformat(log_record[1]),
                "flight_hours": float(log_record[2])
            }
        return None

    def get_leave_booking_record(self, staff_member_id: int, leave_date: date) -> dict | None:
        leave_record = self.__pilot_repository.get_leave_record_by_staff_member_id_and_date(staff_member_id, leave_date)
        if leave_record:
            return {
                "staff_member_id": leave_record[0],
                "leave_date": date.fromisoformat(leave_record[1]),
                "leave_type": leave_record[2]
            }
        return None

    def get_log_record_choices(self, staff_member_id: int) -> list:
        records = self.__pilot_repository.get_flight_logs_by_staff_member_id(staff_member_id)
        
        record_choices = []
        if records:
            for record in records:
                effective_date = datetime.strptime(record["effective_date"], "%Y-%m-%d").strftime("%d/%m/%Y")
                record_choices.append((effective_date, f"{effective_date}: {record['flight_hours']} hrs"))

        return record_choices

    def get_pilot_schedule(self, staff_member_id: int) -> str:
        results = self.__pilot_repository.get_pilot_schedule_by_id(staff_member_id)
        return self.get_schedule_view(results)

    def search_pilots(self, field_name: str, value) -> list[Pilot]:
        return self.__pilot_repository.search_on_field(field_name, value)

    def get_pilot_by_id(self, id: int):
        return self.__pilot_repository.get_pilot_by_id(id)
    
    def get_results_view(self, pilots: list) -> str:
        if pilots is None or len(pilots) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Staff member ID",
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
                pilot.staff_member_id,
                pilot.family_name,
                pilot.first_name,
                pilot.employee_number,
                pilot.employment_status,
                pilot.employment_start_date.strftime("%d/%m/%Y"),
                pilot.employment_end_date.strftime("%d/%m/%Y") if pilot.employment_end_date else '',
                pilot.license_number if pilot.license_number else '',
                pilot.license_type if pilot.license_type else '',
                pilot.license_expiration_date.strftime("%d/%m/%Y") if pilot.license_expiration_date else '',
            ])
        return format_table(table)
    
    def get_schedule_view(self, flights: list) -> str:
        if flights is None or len(flights) == 0:
            return ""
        
        # Initialise the table
        table = PrettyTable([
            "Flight number",
            "Flight status",
            "Dept. (scheduled)",            
            "From",
            "To",
            "Arr. (scheduled)",
            "Pilot role"
        ])

        # Populate table rows
        for row in flights:
            # Format fields
            departure_date_formatted = datetime.strptime(row['scheduled_departure_date'],"%Y-%m-%d").strftime("%d/%m/%Y")
            arrival_date_formatted = datetime.strptime(row['scheduled_arrival_date'],"%Y-%m-%d").strftime("%d/%m/%Y")
            departure = f"{departure_date_formatted}\n{row['scheduled_departure_time']}"
            arrival = f"{arrival_date_formatted}\n{row['scheduled_arrival_time']}"

            table.add_row([
                row["flight_number"],
                row["flight_status"],
                departure,
                row["origin_location"],
                row["destination_location"],
                arrival,
                row["pilot_role"]               
            ])
        return format_table(table)

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
        return format_table(table)
    
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
        return format_table(table)

    def display_record(self, pilot: Pilot) -> str:
        return f"\n> Pilot ID: {pilot.staff_member_id}\n> First name: {pilot.first_name}\n> Family name: {pilot.family_name}"