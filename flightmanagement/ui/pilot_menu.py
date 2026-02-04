from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from datetime import datetime, date
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.models.pilot import Pilot

class PilotMenu:

    __MENU_NAME = "Main -> Manage Pilots"
    __MENU_OPTIONS = [
        ("show", "Show all pilots"),
        ("search", "Search pilots"),
        ("add", "Add a pilot"),
        ("update", "Update a pilot"),
        ("update_time_logs", "Update flight time logs"),
        ("update_leave_bookings", "Update leave bookings"),
        ("delete", "Remove a pilot"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn = None, pilot_service = None):
        self.__pilot_service = pilot_service or PilotService(conn)
        self.__session = session
        self.__bindings = bindings

    def load(self):
        while True:
            __choose_menu = choice(message = format_title(self.__MENU_NAME), options = self.__MENU_OPTIONS)

            if __choose_menu == "show":
                self.__show_option()
            elif __choose_menu == "search":                
                if not self.__search_option():
                    print("\nSearch cancelled.\n")
                    continue
            elif __choose_menu == "add":
                if not self.__add_option():
                    print("\nAction cancelled.\n")
                    continue
            elif __choose_menu == "update":
                if not self.__update_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "update_time_logs":
                if not self.__update_time_logs_option():
                    print("\nAction cancelled.\n")
                    continue
            elif __choose_menu == "update_leave_bookings":
                if not self.__update_leave_bookings_option():
                    print("\nAction cancelled.\n")
                    continue
            elif __choose_menu == "delete":
                if not self.__delete_option():
                    print("\nDelete cancelled.\n")
                    continue
            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice.")

    def __show_option(self) -> None:
        print("\n>> Displaying all pilots\n")
        print(self.__pilot_service.get_pilot_table())

    def __search_option(self) -> bool:
        print("\n>> Search for a pilot (or hit CTRL+C to cancel)\n")

        family_name = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter a family name: ",
            allow_blank = True
        )        
        if family_name.is_cancelled:
            return False

        result = self.__pilot_service.search_pilots("family_name", family_name.value)

        if len(result) == 0:
            print("\n     No matching results.")
        else:
            print(f"\n     {len(result)} match(es) found:\n")
            print(self.__pilot_service.get_results_view(result))

        return True

    def __add_option(self) -> bool:
        print("\n>> Add a pilot (or hit CTRL+C to cancel)\n")

        # Prompt the user to complete fields
        new = self.__prompt_add_pilot()
        if new is None: # Process was cancelled by the user
            return False
        
        try:
            self.__pilot_service.add_pilot(new)
            print("\nNew record successfully added.\n")
        except:
            print("\nError adding pilot.\n")
       
        return True

    def __update_option(self) -> bool:
        print("\n>> Update a pilot (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to edit
        pilot = self.__get_pilot_from_selection()
        if pilot is None or pilot.staff_id is None:
            return False

        print(f"\nEditing information (pilot ID {pilot.staff_id})\n")

        # Prompt the user to edit fields
        update = self.__prompt_update_pilot(pilot)
        if update is None: # Process was cancelled by the user
            return False
        
        try:
            self.__pilot_service.update_pilot(update)
            print("\nRecord successfully updated.\n")
        except:
            print("\nError updating pilot.\n")
            
        return True

    def __update_time_logs_option(self) -> bool:
        print("\n>> Update flight time logs (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot
        pilot = self.__get_pilot_from_selection()

        if pilot is None or pilot.staff_id is None:
            return False

        print(f"\nLog records for {pilot.first_name} {pilot.family_name}:\n")
        print(self.__pilot_service.get_flight_logs_table(pilot.staff_id))

        while True:
            option = UserPrompt(
                session = self.__session,
                prompt_type = "choice",
                prompt = "What would you like to do?\n",
                options = [
                    (1, ("Add a time log record")),
                    (2, ("Update a time log record")),
                    (3, ("Delete a time log record")),
                    (4, ("Back to pilot menu"))
                ],
                key_bindings = self.__bindings
            )
            if option.is_cancelled:
                return False
            print()

            if option.value == 1:            
                record_to_add = self.__prompt_add_time_log_record(pilot.staff_id)
                if record_to_add is None: # Process was cancelled by the user
                    print("\nAction cancelled.\n")
                    continue

                try:
                    self.__pilot_service.add_time_log_record(pilot.staff_id, record_to_add[0], record_to_add[1])
                    print("\nFlight time log record successfully added:\n")
                    print(self.__pilot_service.get_flight_logs_table(pilot.staff_id))
                except:
                    print("\nError adding log record.\n")
            
            elif option.value == 2:
                record_to_update = self.__prompt_update_time_log_record(pilot.staff_id)
                if record_to_update is None: # Process was cancelled by the user
                    print("\nAction cancelled.\n")
                    continue

                try:
                    self.__pilot_service.update_time_log_record(pilot.staff_id, record_to_update[0], record_to_update[1])
                    print("\nFlight time log record successfully removed:\n")
                    print(self.__pilot_service.get_flight_logs_table(pilot.staff_id))
                except:
                    print("\nError updating log record.\n")

            elif option.value == 3:
                record_to_delete = self.__prompt_delete_time_log_record(pilot.staff_id)
                if record_to_delete is None: # Process was cancelled by the user
                    print("\nAction cancelled.\n")
                    continue

                try:
                    self.__pilot_service.delete_time_log_record(pilot.staff_id, record_to_delete)
                    print("\nFlight time log record successfully removed:\n")
                    print(self.__pilot_service.get_flight_logs_table(pilot.staff_id))
                except:
                    print("\nError removing log record.\n")
            
            elif option.value == 4:
                break

        return True

    def __update_leave_bookings_option(self) -> bool:
        print("\n>> Update staff leave bookings (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot
        pilot = self.__get_pilot_from_selection()

        if pilot is None or pilot.staff_id is None:
            return False

        print(f"\nLeave bookings for {pilot.first_name} {pilot.family_name}:\n")
        print(self.__pilot_service.get_leave_bookings_table(pilot.staff_id))

        while True:
            option = UserPrompt(
                session = self.__session,
                prompt_type = "choice",
                prompt = "What would you like to do?\n",
                options = [
                    (1, ("Add a leave booking")),
                    (2, ("Update a leave booking")),
                    (3, ("Delete a leave booking")),
                    (4, ("Back to pilot menu"))
                ],
                key_bindings = self.__bindings
            )
            if option.is_cancelled:
                return False
            print()

            if option.value == 1:            
                record_to_add = self.__prompt_add_leave_booking_record(pilot.staff_id)
                if record_to_add is None: # Process was cancelled by the user
                    print("\nAction cancelled.\n")
                    continue

                try:
                    self.__pilot_service.add_leave_booking_record(pilot.staff_id, record_to_add[0], record_to_add[1])
                    print("\nLeave booking successfully added:\n")
                    print(self.__pilot_service.get_leave_bookings_table(pilot.staff_id))
                except:
                    print("\nError adding leave booking.\n")
            
            elif option.value == 2:
                record_to_update = self.__prompt_update_leave_booking_record(pilot.staff_id)
                if record_to_update is None: # Process was cancelled by the user
                    print("\nAction cancelled.\n")
                    continue

                try:
                    self.__pilot_service.update_leave_booking_record(pilot.staff_id, record_to_update[0], record_to_update[1])
                    print("\nLeave booking successfully removed:\n")
                    print(self.__pilot_service.get_leave_bookings_table(pilot.staff_id))
                except:
                    print("\nError updating leave booking.\n")

            elif option.value == 3:
                record_to_delete = self.__prompt_delete_leave_booking_record(pilot.staff_id)
                if record_to_delete is None: # Process was cancelled by the user
                    print("\nAction cancelled.\n")
                    continue

                try:
                    self.__pilot_service.delete_leave_booking_record(pilot.staff_id, record_to_delete)
                    print("\nLeave booking successfully removed:\n")
                    print(self.__pilot_service.get_leave_bookings_table(pilot.staff_id))
                except:
                    print("\nError removing leave booking.\n")
            
            elif option.value == 4:
                break

        return True
    
    def __delete_option(self) -> bool:
        print("\n>> Delete a pilot (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to delete
        pilot = self.__prompt_delete_pilot()
        if pilot is None:
            return False
        
        # Delete the pilot
        try:
            self.__pilot_service.delete_pilot(pilot)
            print("\nRecord successfully deleted.\n")
        except:
            print("\nError deleting pilot.\n")
        
        return True

    def __prompt_add_pilot(self) -> Pilot | None:

        first_name = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter a first name: ",
            allow_blank = False
        )        
        if first_name.is_cancelled:
            return None
        
        family_name = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter a family name: ",
            allow_blank = False
        )        
        if family_name.is_cancelled:
            return None
        
        employee_number = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter the employee number: ",
            allow_blank = False
        )        
        if employee_number.is_cancelled:
            return None
        
        employment_start_date = UserPrompt(
            session = self.__session,
            prompt_type = "date",
            prompt = "Enter the employment start date (DD/MM/YYYY): ",
            allow_blank = False
        )        
        if employment_start_date.is_cancelled:
            return None

        license_number = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter the pilot license number: ",
            allow_blank = True
        )        
        if license_number.is_cancelled:
            return None

        license_type = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter the pilot license type: ",
            allow_blank = True
        )        
        if license_type.is_cancelled:
            return None

        license_expiration_date = UserPrompt(
            session = self.__session,
            prompt_type = "date",
            prompt = "Enter the license expiry date (DD/MM/YYYY): ",
            allow_blank = True
        )        
        if license_expiration_date.is_cancelled:
            return None

        return Pilot(
            first_name = first_name.value,
            family_name = family_name.value,
            employee_number = employee_number.value,
            employment_status = "Current",
            employment_start_date = datetime.strptime(employment_start_date.value, "%Y-%m-%d"),
            license_number = license_number.value,
            license_type = license_type.value,
            license_expiration_date = datetime.strptime(license_expiration_date.value, "%Y-%m-%d") if len(license_expiration_date.value) > 0 else None
        )

    def __prompt_update_pilot(self, pilot: Pilot) -> Pilot | None:

        first_name = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter a first name: ",
            allow_blank = False,
            default_value = pilot.first_name
        )        
        if first_name.is_cancelled:
            return None
        
        family_name = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter a family name: ",
            allow_blank = False,
            default_value = pilot.family_name
        )        
        if family_name.is_cancelled:
            return None
        print()

        employment_status = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Select an employment status:\n",
            options = [
                ("Current", ("Current")),
                ("Left", ("Left"))
            ],
            key_bindings = self.__bindings,
            default_value = pilot.employment_status
        )
        if employment_status.is_cancelled:
            return None
        print()

        employee_number = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter the employee number: ",
            allow_blank = False,
            default_value = pilot.employee_number
        )        
        if employee_number.is_cancelled:
            return None

        employment_start_date = UserPrompt(
            session = self.__session,
            prompt_type = "date",
            prompt = "Enter the employment start date (DD/MM/YYYY): ",
            allow_blank = False,
            default_value = pilot.employment_start_date.strftime("%d/%m/%Y")
        )        
        if employment_start_date.is_cancelled:
            return None
        
        employment_end_date = UserPrompt(
            session = self.__session,
            prompt_type = "date",
            prompt = "Enter the employment end date (DD/MM/YYYY): ",
            allow_blank = True,
            default_value = pilot.employment_end_date.strftime("%d/%m/%Y") if pilot.employment_end_date else None
        )        
        if employment_end_date.is_cancelled:
            return None

        license_number = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter the pilot license number: ",
            allow_blank = True,
            default_value = pilot.license_number
        )        
        if license_number.is_cancelled:
            return None

        license_type = UserPrompt(
            session = self.__session,
            prompt_type = "text",
            prompt = "Enter the pilot license type: ",
            allow_blank = True,
            default_value = pilot.license_type
        )        
        if license_type.is_cancelled:
            return None

        license_expiration_date = UserPrompt(
            session = self.__session,
            prompt_type = "date",
            prompt = "Enter the license expiry date (DD/MM/YYYY): ",
            allow_blank = True,
            default_value = pilot.license_expiration_date.strftime("%d/%m/%Y") if pilot.license_expiration_date else None
        )        
        if license_expiration_date.is_cancelled:
            return None

        return Pilot(
            staff_id = pilot.staff_id,
            first_name = first_name.value,
            family_name = family_name.value,
            employee_number = employee_number.value,
            employment_status = employment_status.value,
            employment_start_date = datetime.strptime(employment_start_date.value, "%Y-%m-%d"),
            employment_end_date = datetime.strptime(employment_end_date.value, "%Y-%m-%d") if len(employment_end_date.value) > 0 else None,
            license_number = license_number.value,
            license_type = license_type.value,
            license_expiration_date = datetime.strptime(license_expiration_date.value, "%Y-%m-%d") if len(license_expiration_date.value) > 0 else None
        )

    def __prompt_delete_pilot(self) -> Pilot | None:

        # Prompt for the pilot to delete
        pilot = self.__get_pilot_from_selection()
        if pilot is None or pilot.staff_id is None:
            return None
        
        # Prompt for confirmation and delete if confirmed
        confirm = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Are you sure you want to delete this record?\n",
            options = [(1, "yes"),(0, "no")],
            key_bindings = self.__bindings
        )

        if confirm.is_cancelled or confirm.value == False:
            return None
        
        return pilot

    def __prompt_add_time_log_record(self, staff_id: int) -> tuple | None:
        while True:
            effective_date = UserPrompt(
                session = self.__session,
                prompt_type = "date",
                prompt = "Enter the effective date: ",
                allow_blank = False,
                key_bindings = self.__bindings
            )
            if effective_date.is_cancelled:
                return None
            
            if not self.__pilot_service.log_record_exists(staff_id, date.fromisoformat(effective_date.value)):
                break
            print("The pilot already has a log record for this date. Please try again.")

        flight_hours = UserPrompt(
            session = self.__session,
            prompt_type = "float",
            prompt = "Enter the flight hours to log: ",
            allow_blank = False,
            key_bindings = self.__bindings
        )
        if flight_hours.is_cancelled:
            return None
            
        return date.fromisoformat(effective_date.value), float(flight_hours.value)

    def __prompt_update_time_log_record(self, staff_id: int) -> tuple | None:
        
        effective_date = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Choose a record to update:\n",
            options = self.__pilot_service.get_log_record_choices(staff_id),
            key_bindings = self.__bindings
        )
        if effective_date.is_cancelled:
            return None
        print()

        log_record = self.__pilot_service.get_time_log_record(staff_id, date.fromisoformat(effective_date.value))

        flight_hours = UserPrompt(
            session = self.__session,
            prompt_type = "float",
            prompt = "Enter the flight hours to log: ",
            allow_blank = False,
            default_value = log_record["flight_hours"] if log_record else None,
            key_bindings = self.__bindings
        )
        if flight_hours.is_cancelled:
            return None
            
        return date.fromisoformat(effective_date.value), float(flight_hours.value)

    def __prompt_delete_time_log_record(self, staff_id: int) -> date | None:

        effective_date = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Choose a record to delete:\n",
            options = self.__pilot_service.get_log_record_choices(staff_id),
            key_bindings = self.__bindings
        )
        if effective_date.is_cancelled:
            return None

        # Prompt for confirmation and delete if confirmed
        confirm = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Are you sure you want to delete this record?\n",
            options = [(1, "yes"),(0, "no")],
            key_bindings = self.__bindings
        )

        if confirm.is_cancelled or confirm.value == False:
            return None

        return date.fromisoformat(effective_date.value)

    def __prompt_add_leave_booking_record(self, staff_id: int) -> tuple | None:
        while True:
            leave_date = UserPrompt(
                session = self.__session,
                prompt_type = "date",
                prompt = "Enter the leave date: ",
                allow_blank = False,
                key_bindings = self.__bindings
            )
            if leave_date.is_cancelled:
                return None
            
            if not self.__pilot_service.leave_record_exists(staff_id, date.fromisoformat(leave_date.value)):
                break
            print("The staff member already has a leave booking for this date. Please try again.")

        leave_type = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Enter the leave type: \n",
            options = [
                ("Annual leave", ("Annual leave")),
                ("Sick leave", ("Sick leave")),
                ("Parental leave", ("Parental leave")),
                ("Compassionate leave", ("Compassionate leave")),
                ("Study leave", ("Study leave"))
            ],
            key_bindings = self.__bindings
        )
        if leave_type.is_cancelled:
            return None
        print()

        return date.fromisoformat(leave_date.value), leave_type.value

    def __prompt_update_leave_booking_record(self, staff_id: int) -> tuple | None:
        
        leave_date = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Choose a record to update:\n",
            options = self.__pilot_service.get_leave_record_choices(staff_id),
            key_bindings = self.__bindings
        )
        if leave_date.is_cancelled:
            return None
        print()

        leave_record = self.__pilot_service.get_leave_booking_record(staff_id, date.fromisoformat(leave_date.value))

        leave_type = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Enter the leave type: \n",
            options = [
                ("Annual leave", ("Annual leave")),
                ("Sick leave", ("Sick leave")),
                ("Parental leave", ("Parental leave")),
                ("Compassionate leave", ("Compassionate leave")),
                ("Study leave", ("Study leave"))
            ],
            default_value = leave_record["leave_type"] if leave_record else None,
            key_bindings = self.__bindings
        )
        if leave_type.is_cancelled:
            return None
        print()
            
        return date.fromisoformat(leave_date.value), leave_type.value

    def __prompt_delete_leave_booking_record(self, staff_id: int) -> date | None:

        leave_date = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Choose a record to update:\n",
            options = self.__pilot_service.get_leave_record_choices(staff_id),
            key_bindings = self.__bindings
        )
        if leave_date.is_cancelled:
            return None
        print()

        # Prompt for confirmation and delete if confirmed
        confirm = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Are you sure you want to delete this record?\n",
            options = [(1, "yes"),(0, "no")],
            key_bindings = self.__bindings
        )

        if confirm.is_cancelled or confirm.value == False:
            return None

        return date.fromisoformat(leave_date.value)

    def __get_pilot_from_selection(self) -> Pilot | None:
        pilot_id = UserPrompt(
            session = self.__session,
            prompt_type = "choice",
            prompt = "Choose a pilot:\n",
            options = self.__pilot_service.get_pilot_choices(),
            key_bindings = self.__bindings
        )
        if pilot_id.is_cancelled:
            return None
        print()

        return self.__pilot_service.get_pilot_by_id(int(pilot_id.value))