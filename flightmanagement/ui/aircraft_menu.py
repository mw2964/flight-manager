from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel, format_title
from flightmanagement.services.aircraft_service import AircraftService

class AircraftMenu:

    __MENU_NAME = "Aircraft menu"
    __MENU_OPTIONS = [
        ("show", "Show all aircraft"),
        ("search", "Search aircraft"),
        ("add", "Add an aircraft"),
        ("update", "Update an aircraft"),
        ("delete", "Remove an aircraft"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__aircraft_service = AircraftService()
        self.__session = session
        self.__bindings = bindings

    def __show_option(self) -> None:
        print("\n>> Displaying all aircraft\n")
        print(self.__aircraft_service.get_aircraft_list())

    def __search_option(self) -> bool:
        print("\n>> Search for an aircraft (or hit CTRL+C to cancel)\n")

        registration = prompt_or_cancel(self.__session, "Enter an aircraft registration: ", "Search cancelled.")
        if registration is None:
            return False

        result = self.__aircraft_service.search_aircraft("registration", registration)
        print(result)
        return True

    def __add_option(self) -> bool:
        print("\n>> Add an aircraft (or hit CTRL+C to cancel)\n")

        registration = prompt_or_cancel(self.__session, "Enter the aircraft registration: ", "Action cancelled.")
        if registration is None:
            return False

        while True:
            try:
                manufacturer_serial_no_string = prompt_or_cancel(self.__session, "Enter the manufacturer serial number: ", "Action cancelled.")
                if manufacturer_serial_no_string:
                    manufacturer_serial_no = int(manufacturer_serial_no_string)
                else:
                    manufacturer_serial_no = None
                break
            except ValueError:
                print("Manufacturer serial number must be a number. Please try again.")
        if manufacturer_serial_no is None:
            return False

        icao_hex = prompt_or_cancel(self.__session, "Enter the ICAO hex code: ", "Action cancelled.")
        if icao_hex is None:
            return False

        manufacturer = prompt_or_cancel(self.__session, "Enter the manufacturer: ", "Action cancelled.")
        if manufacturer is None:
            return False

        model = prompt_or_cancel(self.__session, "Enter the model: ", "Action cancelled.")
        if model is None:
            return False

        icao_type = prompt_or_cancel(self.__session, "Enter the ICAO type: ", "Action cancelled.")
        if icao_type is None:
            return False

        status = prompt_or_cancel(self.__session, "Enter the aircraft status: ", "Action cancelled.")
        if status is None:
            return False

        print()
        self.__aircraft_service.add_aircraft(registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        return True

    def __update_option(self) -> bool:
        print("\n>> Update an aircraft (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose an aircraft to update: ",
            options=self.__aircraft_service.get_aircraft_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            print("\nUpdate cancelled.")
            return False

        # Retrieve the aircraft record
        aircraft = self.__aircraft_service.get_aircraft_by_id(id)

        if aircraft:

            print(f"\nEditing information (aircraft ID {id})\n")

            registration = prompt_or_cancel(self.__session, "Registration: ", "Update cancelled", aircraft.registration)
            if registration is None:
                return False
            
            while True:
                try:
                    manufacturer_serial_no_string = prompt_or_cancel(self.__session, "Manufacturer serial number: ", "Update cancelled.", str(aircraft.manufacturer_serial_no))
                    if manufacturer_serial_no_string:
                        manufacturer_serial_no = int(manufacturer_serial_no_string)
                    else:
                        manufacturer_serial_no = None
                    break
                except ValueError:
                    print("Manufacturer serial number must be a number. Please try again.")
            if manufacturer_serial_no is None:
                return False

            icao_hex = prompt_or_cancel(self.__session, "ICAO hex code: ", "Update cancelled.", aircraft.icao_hex)
            if icao_hex is None:
                return False

            manufacturer = prompt_or_cancel(self.__session, "Manufacturer: ", "Update cancelled.", aircraft.manufacturer)
            if manufacturer is None:
                return False

            model = prompt_or_cancel(self.__session, "Model: ", "Update cancelled.", aircraft.model)
            if model is None:
                return False

            icao_type = prompt_or_cancel(self.__session, "ICAO type: ", "Update cancelled.", aircraft.icao_type)
            if icao_type is None:
                return False
            
            print()
            status = choice(
                message="Select an aircraft status: ",
                options=[
                    ("Active", ("Active")),
                    ("Inactive", ("Inactive")),
                    ("Decommissioned", ("Decommissioned"))
                ],
                default=aircraft.status,
                key_bindings=self.__bindings
            )
            if status == "__CANCEL__":
                print("\nUpdate cancelled.")
                return False
            
            print()
            self.__aircraft_service.update_aircraft(id, registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        
        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete an aircraft (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose an aircraft to delete: ",
            options=self.__aircraft_service.get_aircraft_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            print("\nDelete cancelled.")
            return False

        print()
        if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
            print()
            self.__aircraft_service.delete_aircraft(id)
        else:
            print("\nDelete cancelled.")

        return True

    def load(self):

        while True:

            __choose_menu = choice(
                message=format_title(self.__MENU_NAME),
                options=self.__MENU_OPTIONS
            )

            if __choose_menu == "show":
                self.__show_option()
            elif __choose_menu == "search":                
                if not self.__search_option():
                    continue
            elif __choose_menu == "add":
                if not self.__add_option():
                    continue
            elif __choose_menu == "update":
                if not self.__update_option():
                    continue
            elif __choose_menu == "delete":
                if not self.__delete_option():
                    continue
            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice")
    