from prompt_toolkit.shortcuts import choice
from typing import Union
from flightmanagement.error import FieldValidationError, DomainValidationError, UserCancelled, MissingData, DependentRecords, DuplicateRecord, InvalidData
from flightmanagement.ui.base_menu import BaseMenu, Unset
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.models.aircraft import Aircraft

class AircraftMenu(BaseMenu):

    def __init__(self, session, bindings, conn = None, aircraft_service = None):
        super().__init__(session, bindings, conn)

        self._aircraft_service = aircraft_service or AircraftService(conn)
        self._menu_name = "Main -> Manage Aircraft"
        self._menu_options = [
            ("show", "Show all aircraft"),
            ("search", "Search aircraft"),
            ("add", "Add an aircraft"),
            ("update", "Update an aircraft"),
            ("delete", "Remove an aircraft"),
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
                elif _selected_option == "delete":
                    self._delete_option()
                elif _selected_option == "back":
                    return
            except UserCancelled as e:
                print(e)
                continue

    def _show_option(self) -> None:
        print("\n>> Displaying all aircraft\n")
        print(self._aircraft_service.get_aircraft_table())

    def _search_option(self) -> None:
        print("\n>> Search for an aircraft (or hit CTRL+C to cancel)\n")

        registration = self._prompt_until_valid(
            prompt_text = "Aircraft registration:",
            getter = lambda p: p.get_str(),
            field = "registration"
        )

        result = self._aircraft_service.search_aircraft("registration", registration)
        print(self._format_results_text(len(result), self._aircraft_service.get_results_view(result)))

    def _add_option(self) -> None:
        print("\n>> Add an aircraft (or hit CTRL+C to cancel)\n")

        new = self._prompt_add_aircraft()

        try:
            new_id = self._aircraft_service.add_aircraft(new)
            print(f"\nNew aircraft successfully added (aircraft ID: {new_id}).\n")
        except MissingData as e:
            print("\nRecord insert failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord insert failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord insert failed: invalid information.")

    def _update_option(self) -> None:
        print("\n>> Update an aircraft (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to edit
        aircraft = self._get_aircraft_from_selection()
        print(f"\nEditing information (aircraft ID {aircraft.aircraft_id})\n")

        update = self._prompt_update_aircraft(aircraft)

        try:
            self._aircraft_service.update_aircraft(update)
            print("\nRecord successfully updated.\n")
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")

    def _delete_option(self) -> None:
        print("\n>> Delete an aircraft (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to delete
        aircraft = self._prompt_delete_aircraft()
        
        # Delete the aircraft
        try:
            self._aircraft_service.delete_aircraft(aircraft)
            print("\nRecord successfully deleted.\n")
        except DependentRecords as e:
            print("\nCannot delete aircraft while there are still related flight records.")
        
    def _prompt_add_aircraft(self) -> Aircraft:
        
        unset = Unset()

        aircraft_type_id: Union[int, None, Unset] = unset
        registration: Union[str, None, Unset] = unset
        manufacturer_serial_no: Union[int, None, Unset] = unset
        icao_hex: Union[str, None, Unset] = unset
        aircraft_status: Union[str, None, Unset] = unset

        while True:
            try:
                if aircraft_type_id is unset:
                    aircraft_type_id = self._prompt_until_valid(
                        prompt_text = "Select an aircraft type:",
                        getter = lambda p: p.get_int(),
                        field = "aircraft_type_id",
                        required = True,                       
                        is_picklist = True,                        
                        options = self._aircraft_service.get_aircraft_type_choices()
                    )
                    print()

                if registration is unset:
                    registration = self._prompt_until_valid(
                        prompt_text = "Aircraft registration:",
                        getter = lambda p: p.get_str(),
                        field = "registration",
                        required = True
                    )

                if manufacturer_serial_no is unset:
                    manufacturer_serial_no = self._prompt_until_valid(
                        prompt_text = "Manufacturer serial number:",
                        getter = lambda p: p.get_int(),
                        field = "manufacturer_serial_no"
                    )

                if icao_hex is unset:
                    icao_hex = self._prompt_until_valid(
                        prompt_text = "ICAO hex code:",
                        getter = lambda p: p.get_str(),
                        field = "icao_hex"
                    )

                if aircraft_status is unset:
                    print()
                    aircraft_status = self._prompt_until_valid(
                        prompt_text="Select an aircraft status:",
                        getter = lambda p: p.get_str(),                                
                        is_picklist=True,
                        options=[
                            ("Active", "Active"),
                            ("Inactive", "Inactive"),
                            ("Decommissioned", "Decommissioned"),
                        ],
                        field = "aircraft_status"
                    )
                    print()

                return Aircraft(
                    aircraft_type_id = self._required(aircraft_type_id, "aircraft_type_id"),
                    registration = self._required(registration, "registration"),
                    manufacturer_serial_no = self._optional(manufacturer_serial_no),
                    icao_hex = self._optional(icao_hex),
                    aircraft_status = self._required(aircraft_status, "aircraft_status")
                )
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))
                print()

                if e.field == "registration":
                    registration = unset
                elif e.field == "manufacturer_serial_no":
                    manufacturer_serial_no = unset
                elif e.field == "icao_hex":
                    icao_hex = unset
                elif e.field == "aircraft_type_id":
                    aircraft_type_id = unset
                elif e.field == "aircraft_status":
                    aircraft_status = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))
                print()

                aircraft_type_id = unset
                registration = unset
                manufacturer_serial_no = unset
                icao_hex = unset
                aircraft_status = unset

    def _prompt_update_aircraft(self, aircraft: Aircraft) -> Aircraft:

        unset = Unset()

        aircraft_type_id: Union[int, None, Unset] = unset
        registration: Union[str, None, Unset] = unset
        manufacturer_serial_no: Union[int, None, Unset] = unset
        icao_hex: Union[str, None, Unset] = unset
        aircraft_status: Union[str, None, Unset] = unset

        while True:
            try:
                if aircraft_type_id is unset:
                    aircraft_type_id = self._prompt_until_valid(
                        prompt_text = "Select an aircraft type:",
                        getter = lambda p: p.get_int(),
                        field = "aircraft_type_id",
                        required = True,
                        is_picklist = True,
                        options = self._aircraft_service.get_aircraft_type_choices(),
                        default_value = aircraft.aircraft_type_id
                    )
                    print()

                if registration is unset:
                    registration = self._prompt_until_valid(
                        prompt_text = "Aircraft registration:",
                        getter = lambda p: p.get_str(),
                        field = "registration",
                        required = True,
                        default_value = aircraft.registration
                    )

                if manufacturer_serial_no is unset:
                    manufacturer_serial_no = self._prompt_until_valid(
                        prompt_text = "Manufacturer serial number:",
                        getter = lambda p: p.get_int(),
                        field = "manufacturer_serial_no",
                        default_value = aircraft.manufacturer_serial_no
                    )

                if icao_hex is unset:
                    icao_hex = self._prompt_until_valid(
                        prompt_text = "ICAO hex code:",
                        getter = lambda p: p.get_str(),
                        field = "icao_hex",
                        default_value = aircraft.icao_hex
                    )
                
                if aircraft_status is unset:
                    print()
                    aircraft_status = self._prompt_until_valid(
                        prompt_text="Select an aircraft status:",
                        getter = lambda p: p.get_str(),
                        field = "aircraft_status",
                        required = True,
                        is_picklist=True,
                        options=[
                            ("Active", "Active"),
                            ("Inactive", "Inactive"),
                            ("Decommissioned", "Decommissioned"),
                        ],
                        default_value = aircraft.aircraft_status
                    )
                    print()

                return Aircraft(
                    aircraft_id = aircraft.aircraft_id,
                    aircraft_type_id = self._required(aircraft_type_id, "aircraft_type_id"),
                    registration = self._required(registration, "registration"),
                    manufacturer_serial_no = self._optional(manufacturer_serial_no),
                    icao_hex = self._optional(icao_hex),
                    aircraft_status = self._required(aircraft_status, "aircraft_status")
                )
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "registration":
                    registration = unset
                elif e.field == "manufacturer_serial_no":
                    manufacturer_serial_no = unset
                elif e.field == "icao_hex":
                    icao_hex = unset
                elif e.field == "aircraft_type_id":
                    aircraft_type_id = unset
                elif e.field == "aircraft_status":
                    aircraft_status = unset
            
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                aircraft_type_id = unset
                registration = unset
                manufacturer_serial_no = unset
                icao_hex = unset
                aircraft_status = unset
            
    def _prompt_delete_aircraft(self) -> Aircraft:

        # Prompt for the aircraft to delete
        aircraft = self._get_aircraft_from_selection()
        print()

        # Delete will be cancelled if the user doesn't confirm
        self._prompt_delete_confirmation()

        return aircraft

    def _get_aircraft_from_selection(self) -> Aircraft:
        
        aircraft_id = None

        while aircraft_id is None:
            aircraft_id = self._prompt_until_valid(
                prompt_text = "Select an aircraft:",
                getter = lambda p: p.get_int(),
                field = "aircraft_id",
                required = True,
                is_picklist = True,
                options = self._aircraft_service.get_aircraft_choices()
            )

        aircraft = self._aircraft_service.get_aircraft_by_id(aircraft_id)

        if aircraft is None:
            raise ValueError("No aircraft returned from selection.")
        
        if aircraft.aircraft_id is None:
            raise ValueError("Selected aircraft missing unique identifier.")

        return aircraft