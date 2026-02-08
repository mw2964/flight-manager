from prompt_toolkit.shortcuts import choice
from typing import Union
from datetime import date
from flightmanagement.error import FieldValidationError, DomainValidationError, UserCancelled, MissingData, DependentRecords, DuplicateRecord, InvalidData
from flightmanagement.ui.base_menu import BaseMenu, Unset
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.models.pilot import Pilot

class PilotMenu(BaseMenu):

    def __init__(self, session, bindings, conn = None, pilot_service = None):
        super().__init__(session, bindings, conn)
        
        self._pilot_service = pilot_service or PilotService(conn)
        self._menu_name = "Main -> Manage Pilots"
        self._menu_options = [
            ("show", "Show all pilots"),
            ("search", "Search pilots"),
            ("add", "Add a pilot"),
            ("update", "Update a pilot"),
            ("view_schedule", "View pilot flight schedule"),
            ("update_time_logs", "Update flight time logs"),
            ("update_leave_bookings", "Update leave bookings"),
            ("delete", "Remove a pilot"),
            ("back", "Back to main menu")
        ]

    def load(self):
        while True:
            _selected_option = choice(message = self._format_title(self._menu_name), options = self._menu_options)

            try:
                if _selected_option == "show":
                    self._show_option()
                elif _selected_option == "search":                
                    self._search_option()
                elif _selected_option == "add":
                    self._add_option()
                elif _selected_option == "update":
                    self._update_option()
                elif _selected_option == "view_schedule":
                    self._view_schedule_option()
                elif _selected_option == "update_time_logs":
                    self._update_time_logs_option()
                elif _selected_option == "update_leave_bookings":
                    self._update_leave_bookings_option()
                elif _selected_option == "delete":
                    self._delete_option()
                elif _selected_option == "back":
                    return                
            except UserCancelled as e:
                print(e)
                continue

    def _show_option(self) -> None:
        print("\n>> Displaying all pilots\n")
        print(self._pilot_service.get_pilot_table())

    def _search_option(self) -> None:
        print("\n>> Search for a pilot (or hit CTRL+C to cancel)\n")

        family_name = self._prompt_until_valid(
                prompt_text = "Family name:",
                getter = lambda p: p.get_str(),
                field = "family_name"
            )
        result = self._pilot_service.search_pilots("family_name", family_name)
        print(self._format_results_text(len(result), self._pilot_service.get_results_view(result)))        

    def _add_option(self) -> None:
        print("\n>> Add a pilot (or hit CTRL+C to cancel)\n")

        new = self._prompt_add_pilot()

        try:
            new_id = self._pilot_service.add_pilot(new)
            print(f"\nNew record successfully added (staff ID: {new_id}).\n")
        except MissingData as e:
            print("\nRecord insert failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord insert failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord insert failed: invalid information.")
       
    def _update_option(self) -> None:
        print("\n>> Update a pilot (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to edit
        pilot = self._get_pilot_from_selection()
        print(f"\nEditing information (staff ID {pilot.staff_id})\n")

        update = self._prompt_update_pilot(pilot)

        try:
            self._pilot_service.update_pilot(update)
            print("\nRecord successfully updated.\n")
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")

    def _view_schedule_option(self) -> None:
        print("\n>> View a pilot's flight schedule (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to edit
        pilot = self._get_pilot_from_selection()
        print(f"\nViewing flight schedule for {pilot.first_name} {pilot.family_name}\n")
        if pilot.staff_id is not None:
            print(self._pilot_service.get_pilot_schedule(pilot.staff_id))
        

    def _update_time_logs_option(self) -> None:
        print("\n>> Update flight time logs (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot
        pilot = self._get_pilot_from_selection()

        if pilot.staff_id is None:
            raise ValueError

        print(f"\nLog records for {pilot.first_name} {pilot.family_name}:\n")
        print(self._pilot_service.get_flight_logs_table(pilot.staff_id))

        while True:

            option = self._prompt_until_valid(
                prompt_text = "What would you like to do?:",
                getter = lambda p: p.get_int(),
                field = "option",
                required = True,
                is_picklist = True,
                options = [
                    (1, ("Add a time log record")),
                    (2, ("Update a time log record")),
                    (3, ("Delete a time log record")),
                    (4, ("Back to pilot menu"))
                ]
            )
            print()

            if option == 1:            
                record_to_add = self._prompt_add_time_log_record(pilot.staff_id)

                try:
                    self._pilot_service.add_time_log_record(pilot.staff_id, record_to_add[0], record_to_add[1])
                    print("\nFlight time log record successfully added:\n")
                except MissingData as e:
                    print("\nRecord insert failed: missing mandatory data.")
                except DuplicateRecord as e:
                    print("\nRecord insert failed: duplicated information.")
                except InvalidData as e:
                    print("\nRecord insert failed: invalid information.")

                print(self._pilot_service.get_flight_logs_table(pilot.staff_id))
            
            elif option == 2:
                record_to_update = self._prompt_update_time_log_record(pilot.staff_id)

                try:
                    self._pilot_service.update_time_log_record(pilot.staff_id, record_to_update[0], record_to_update[1])
                    print("\nFlight time log record successfully updated:\n")
                except MissingData as e:
                    print("\nRecord update failed: missing mandatory data.")
                except DuplicateRecord as e:
                    print("\nRecord update failed: duplicated information.")
                except InvalidData as e:
                    print("\nRecord update failed: invalid information.")

                print(self._pilot_service.get_flight_logs_table(pilot.staff_id))

            elif option == 3:
                record_to_delete = self._prompt_delete_time_log_record(pilot.staff_id)
                self._pilot_service.delete_time_log_record(pilot.staff_id, record_to_delete)
                print("\nFlight time log record successfully removed:\n")
                print(self._pilot_service.get_flight_logs_table(pilot.staff_id))
            
            elif option == 4:
                break

    def _update_leave_bookings_option(self) -> None:
        print("\n>> Update staff leave bookings (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot
        pilot = self._get_pilot_from_selection()

        if pilot.staff_id is None:
            raise ValueError

        print(f"\nLeave bookings for {pilot.first_name} {pilot.family_name}:\n")
        print(self._pilot_service.get_leave_bookings_table(pilot.staff_id))

        while True:

            option = self._prompt_until_valid(
                prompt_text = "What would you like to do?:",
                getter = lambda p: p.get_int(),
                field = "option",
                required = True,
                is_picklist = True,
                options = [
                    (1, ("Add a leave booking")),
                    (2, ("Update a leave booking")),
                    (3, ("Delete a leave booking")),
                    (4, ("Back to pilot menu"))
                ],
            )
            print()

            if option == 1:            
                record_to_add = self._prompt_add_leave_booking_record(pilot.staff_id)

                try:
                    self._pilot_service.add_leave_booking_record(pilot.staff_id, record_to_add[0], record_to_add[1])
                    print("\nLeave booking successfully added:\n")
                except MissingData as e:
                    print("\nRecord insert failed: missing mandatory data.")
                except DuplicateRecord as e:
                    print("\nRecord insert failed: duplicated information.")
                except InvalidData as e:
                    print("\nRecord insert failed: invalid information.")

                print(self._pilot_service.get_leave_bookings_table(pilot.staff_id))
            
            elif option == 2:
                record_to_update = self._prompt_update_leave_booking_record(pilot.staff_id)

                try:
                    self._pilot_service.update_leave_booking_record(pilot.staff_id, record_to_update[0], record_to_update[1])
                    print("\nLeave booking successfully updated:\n")
                except MissingData as e:
                    print("\nRecord update failed: missing mandatory data.")
                except DuplicateRecord as e:
                    print("\nRecord update failed: duplicated information.")
                except InvalidData as e:
                    print("\nRecord update failed: invalid information.")

                print(self._pilot_service.get_leave_bookings_table(pilot.staff_id))

            elif option == 3:
                record_to_delete = self._prompt_delete_leave_booking_record(pilot.staff_id)
                self._pilot_service.delete_leave_booking_record(pilot.staff_id, record_to_delete)
                print("\nLeave booking successfully removed:\n")
                print(self._pilot_service.get_leave_bookings_table(pilot.staff_id))
        
            elif option == 4:
                break
    
    def _delete_option(self) -> None:
        print("\n>> Delete a pilot (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to delete
        pilot = self._prompt_delete_pilot()
        
        # Delete the pilot
        try:
            self._pilot_service.delete_pilot(pilot)
            print("\nRecord successfully deleted.\n")
        except DependentRecords as e:
            print("\nCannot delete pilot while there are still related flight records.")

    def _prompt_add_pilot(self) -> Pilot:

        unset = Unset()

        first_name: Union[str, None, Unset] = unset
        family_name: Union[str, None, Unset] = unset
        employee_number: Union[str, None, Unset] = unset
        employment_start_date: Union[date, None, Unset] = unset
        license_number: Union[str, None, Unset] = unset
        license_type: Union[str, None, Unset] = unset
        license_expiration_date: Union[date, None, Unset] = unset

        while True:
            try:
                if first_name is unset:
                    first_name = self._prompt_until_valid(
                        prompt_text = "First name:",
                        getter = lambda p: p.get_str(),
                        field = "first_name",
                        required = True
                    )
                
                if family_name is unset:
                    family_name = self._prompt_until_valid(
                        prompt_text = "Family name:",
                        getter = lambda p: p.get_str(),
                        field = "first_name",
                        required = True
                    )
                
                if employee_number is unset:
                    employee_number = self._prompt_until_valid(
                        prompt_text = "Employee number:",
                        getter = lambda p: p.get_str(),
                        field = "employee_number"
                    )
                
                if employment_start_date is unset:
                    employment_start_date = self._prompt_until_valid(
                        prompt_text = "Employment start date:",
                        getter = lambda p: p.get_date(),
                        field = "employment_status",
                        required = True
                    )

                if license_number is unset:
                    license_number =self._prompt_until_valid(
                        prompt_text = "License number:",
                        getter = lambda p: p.get_str(),
                        field = "license_number"
                    )

                if license_type is unset:
                    license_type = self._prompt_until_valid(
                        prompt_text = "License type:",
                        getter = lambda p: p.get_str(),
                        field = "license_type"
                    )

                if license_expiration_date is unset:
                    license_expiration_date = self._prompt_until_valid(
                        prompt_text = "License expiration date:",
                        getter = lambda p: p.get_date(),
                        field = "license_expiration_date"
                    )

                return Pilot(
                    first_name = self._required(first_name, "first_name"),
                    family_name = self._required(family_name, "family_name"),
                    employee_number = self._required(employee_number, "employee_number"),
                    employment_status = "Current",
                    employment_start_date = self._required(employment_start_date, "employment_start_date"),
                    license_number = self._optional(license_number),
                    license_type = self._optional(license_type),
                    license_expiration_date = self._optional(license_expiration_date)
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "first_name":
                    first_name = unset
                elif e.field == "family_name":
                    family_name = unset
                elif e.field == "employee_number":
                    employee_number = unset
                elif e.field == "employment_start_date":
                    employment_start_date = unset
                elif e.field == "license_number":
                    license_number = unset
                elif e.field == "license_type":
                    license_type = unset
                elif e.field == "license_expiration_date":
                    license_expiration_date = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                first_name = unset
                family_name = unset
                employee_number = unset
                employment_start_date = unset
                license_number = unset
                license_type = unset
                license_expiration_date = unset

    def _prompt_update_pilot(self, pilot: Pilot) -> Pilot:

        unset = Unset()

        first_name: Union[str, None, Unset] = unset
        family_name: Union[str, None, Unset] = unset
        employment_status: Union[str, None, Unset] = unset
        employee_number: Union[str, None, Unset] = unset
        employment_start_date: Union[date, None, Unset] = unset
        employment_end_date: Union[date, None, Unset] = unset
        license_number: Union[str, None, Unset] = unset
        license_type: Union[str, None, Unset] = unset
        license_expiration_date: Union[date, None, Unset] = unset

        while True:
            try:
                if first_name is unset:
                    first_name = self._prompt_until_valid(
                        prompt_text = "First name:",
                        getter = lambda p: p.get_str(),
                        field = "first_name",
                        required = True,
                        default_value = pilot.first_name
                    )
                
                if family_name is unset:
                    family_name = self._prompt_until_valid(
                        prompt_text = "Family name:",
                        getter = lambda p: p.get_str(),
                        field = "family_name",
                        required = True,
                        default_value = pilot.family_name
                    )
                
                if employment_status is unset:      
                    print()                  
                    employment_status = self._prompt_until_valid(                                
                        prompt_text = "Select an employment status:",
                        is_picklist = True,
                        getter = lambda p: p.get_str(),
                        field = "employment_status",
                        required = True,
                        options = [
                            ("Current", ("Current")),
                            ("Left", ("Left"))
                        ],
                        default_value = pilot.employment_status
                    )
                    print()

                if employee_number is unset:
                    employee_number = self._prompt_until_valid(
                        prompt_text = "Employee number:",
                        getter = lambda p: p.get_str(),
                        field = "employee_number",
                        required = True,
                        default_value = pilot.employee_number
                    )
                
                if employment_start_date is unset:
                    employment_start_date = self._prompt_until_valid(
                        prompt_text = "Employment start date:",
                        getter = lambda p: p.get_date(),
                        field = "employment_start_date",
                        required = True,
                        default_value = pilot.employment_start_date.strftime("%d/%m/%Y")
                    )

                if employment_end_date is unset:
                    employment_end_date = self._prompt_until_valid(
                        prompt_text = "Employment end date:",
                        getter = lambda p: p.get_date(),
                        field = "employment_end_date",
                        default_value = pilot.employment_end_date.strftime("%d/%m/%Y") if pilot.employment_end_date else None
                    )

                if license_number is unset:
                    license_number = self._prompt_until_valid(
                        prompt_text = "License number:",
                        getter = lambda p: p.get_str(),
                        field = "license_number",
                        default_value = pilot.license_number
                    )

                if license_type is unset:
                    license_type = self._prompt_until_valid(
                        prompt_text = "License type:",
                        getter = lambda p: p.get_str(),
                        field = "license_type",
                        default_value = pilot.license_type
                    )

                if license_expiration_date is unset:
                    license_expiration_date = self._prompt_until_valid(
                        prompt_text = "License expiration date:",
                        getter = lambda p: p.get_date(),
                        field = "license_expiration_date",
                        default_value = pilot.license_expiration_date.strftime("%d/%m/%Y") if pilot.license_expiration_date else None
                    )

                return Pilot(
                    staff_id = pilot.staff_id,
                    first_name = self._required(first_name, "first_name"),
                    family_name = self._required(family_name, "family_name"),
                    employee_number = self._required(employee_number, "employee_number"),
                    employment_status = self._required(employment_status, "employment_status"),
                    employment_start_date = self._required(employment_start_date, "employment_start_date"),
                    employment_end_date = self._optional(employment_end_date),
                    license_number = self._optional(license_number),
                    license_type = self._optional(license_type),
                    license_expiration_date = self._optional(license_expiration_date)
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "first_name":
                    first_name = unset
                elif e.field == "family_name":
                    family_name = unset
                elif e.field == "employee_number":
                    employee_number = unset
                elif e.field == "employment_start_date":
                    employment_start_date = unset
                elif e.field == "employment_end_date":
                    employment_end_date = unset
                elif e.field == "employment_status":
                    employment_end_date = unset
                elif e.field == "license_number":
                    license_number = unset
                elif e.field == "license_type":
                    license_type = unset
                elif e.field == "license_expiration_date":
                    license_expiration_date = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                first_name = unset
                family_name = unset
                employment_status = unset
                employee_number = unset
                employment_start_date = unset
                employment_end_date = unset
                license_number = unset
                license_type = unset
                license_expiration_date = unset

    def _prompt_delete_pilot(self) -> Pilot:

        # Prompt for the pilot to delete
        pilot = self._get_pilot_from_selection()
        print()

        # Delete will be cancelled if the user doesn't confirm
        self._prompt_delete_confirmation()

        return pilot

    def _prompt_add_time_log_record(self, staff_id: int) -> tuple:

        effective_date = None
        flight_hours = None

        while True:
            try:
                while effective_date is None:
                    effective_date = self._prompt_until_valid(
                        prompt_text = "Enter the effective date:",
                        getter = lambda p: p.get_date(),
                        field = "effective_date",
                        required = True
                    )
                
                if self._pilot_service.log_record_exists(staff_id, effective_date):
                    raise FieldValidationError("effective_date", "The pilot already has a log record for this date. Please try again.")

                while flight_hours is None:
                    flight_hours = self._prompt_until_valid(                            
                        prompt_text = "Enter the flight hours to log:",
                        getter = lambda p: p.get_float(),
                        field = "flight_hours",
                        required = True
                    )

                return effective_date, flight_hours
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))
                print()

                if e.field == "effective_date":
                    effective_date = None
                elif e.field == "flight_hours":
                    flight_hours = None

            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))
                print()

                effective_date = None
                flight_hours = None

    def _prompt_update_time_log_record(self, staff_id: int) -> tuple:
        
        effective_date = None
        flight_hours = None

        while True:
            try:
                while effective_date is None:
                    effective_date = self._prompt_until_valid(
                        prompt_text = "Choose a record to update:",
                        is_picklist = True,
                        field = "effective_date",
                        required = True,
                        getter = lambda p: p.get_date(),
                        options = self._pilot_service.get_log_record_choices(staff_id)
                    )       
                    print()

                log_record = self._pilot_service.get_time_log_record(staff_id, effective_date)

                while flight_hours is None:
                    flight_hours = self._prompt_until_valid(                            
                        prompt_text = "Enter the flight hours to log:",
                        getter = lambda p: p.get_float(),
                        field = "flight_hours",
                        required = True,
                        default_value = log_record["flight_hours"] if log_record else None
                    )

                return effective_date, flight_hours
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))
                print()

                if e.field == "effective_date":
                    effective_date = None
                elif e.field == "flight_hours":
                    flight_hours = None

            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))
                print()

                effective_date = None
                flight_hours = None

    def _prompt_delete_time_log_record(self, staff_id: int) -> date:

        effective_date = None

        while effective_date is None:
            effective_date = self._prompt_until_valid(
                prompt_text = "Choose a record to update:",
                is_picklist = True,
                field = "effective_date",
                required = True,
                getter = lambda p: p.get_date(),
                options = self._pilot_service.get_log_record_choices(staff_id)
            )                   
            print()

        # Delete will be cancelled if the user doesn't confirm
        self._prompt_delete_confirmation()

        return effective_date

    def _prompt_add_leave_booking_record(self, staff_id: int) -> tuple:
        
        leave_date = None
        leave_type = None

        while True:
            try:
                while leave_date is None:
                    leave_date = self._prompt_until_valid(
                        prompt_text = "Enter the leave date:",
                        getter = lambda p: p.get_date(),
                        field = "leave_date",
                        required = True
                    )
                
                if self._pilot_service.leave_record_exists(staff_id, leave_date):
                    raise FieldValidationError("effective_date", "The staff member already has a leave booking for this date.")

                while leave_type is None:
                    print()
                    leave_type = self._prompt_until_valid(
                        is_picklist = True,                            
                        prompt_text = "Enter the leave type:",
                        getter = lambda p: p.get_str(),
                        field = "leave_type",
                        required = True,
                        options = [
                            ("Annual leave", ("Annual leave")),
                            ("Sick leave", ("Sick leave")),
                            ("Parental leave", ("Parental leave")),
                            ("Compassionate leave", ("Compassionate leave")),
                            ("Study leave", ("Study leave"))
                        ]
                    )
                    print()

                return leave_date, leave_type
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))
                print()

                if e.field == "leave_date":
                    leave_date = None
                elif e.field == "leave_type":
                    leave_type = None

            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))
                print()

                leave_date = None
                leave_type = None
        
    def _prompt_update_leave_booking_record(self, staff_id: int) -> tuple:
        
        leave_date = None
        leave_type = None

        while True:
            try:
                while leave_date is None:
                    leave_date = self._prompt_until_valid(
                        is_picklist = True,
                        getter = lambda p: p.get_date(),
                        field = "leave_date",
                        required = True,
                        prompt_text = "Choose a record to update:",
                        options = self._pilot_service.get_leave_record_choices(staff_id)
                    )
                    print()

                leave_record = self._pilot_service.get_leave_booking_record(staff_id, leave_date)

                while leave_type is None:
                    leave_type = self._prompt_until_valid(
                        is_picklist = True,                            
                        prompt_text = "Enter the leave type:",
                        getter = lambda p: p.get_str(),
                        field = "leave_type",
                        required = True,
                        options = [
                            ("Annual leave", ("Annual leave")),
                            ("Sick leave", ("Sick leave")),
                            ("Parental leave", ("Parental leave")),
                            ("Compassionate leave", ("Compassionate leave")),
                            ("Study leave", ("Study leave"))
                        ],
                        default_value = leave_record["leave_type"] if leave_record else None
                    )
                    print()

                return leave_date, leave_type

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))
                print()

                if e.field == "leave_type":
                    leave_type = None

            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))
                print()

                leave_date = None
                leave_type = None 
        
    def _prompt_delete_leave_booking_record(self, staff_id: int) -> date:

        leave_date = None

        while leave_date is None:
            leave_date = self._prompt_until_valid(
                prompt_text = "Choose a record to update:",
                field = "leave_date",
                required = True,
                is_picklist = True,
                getter = lambda p: p.get_date(),
                options = self._pilot_service.get_leave_record_choices(staff_id)
            )                 
            print()

        # Delete will be cancelled if user doesn't confirm
        self._prompt_delete_confirmation()

        return leave_date

    def _get_pilot_from_selection(self) -> Pilot:

        pilot_id = None

        while pilot_id is None:
            pilot_id = self._prompt_until_valid(
                prompt_text = "Select a pilot:",
                getter = lambda p: p.get_int(),
                field = "pilot_id",
                required = True,
                is_picklist = True,
                options = self._pilot_service.get_pilot_choices()
            )

        pilot = self._pilot_service.get_pilot_by_id(pilot_id)

        if pilot is None:
            raise ValueError("No pilot returned from selection.")
        
        if pilot.staff_id is None:
            raise ValueError("Selected pilot missing unique identifier.")

        return pilot