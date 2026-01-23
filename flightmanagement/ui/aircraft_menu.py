from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.models.aircraft import Aircraft

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

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn=None, aircraft_service=None):
        self.__aircraft_service = aircraft_service or AircraftService(conn)
        self.__session = session
        self.__bindings = bindings

    def load(self):
        while True:
            __choose_menu = choice(message=format_title(self.__MENU_NAME), options=self.__MENU_OPTIONS)

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
            elif __choose_menu == "delete":
                if not self.__delete_option():
                    print("\nDelete cancelled.\n")
                    continue
            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice.")

    def __show_option(self) -> None:
        print("\n>> Displaying all aircraft\n")
        print(self.__aircraft_service.get_aircraft_table())

    def __search_option(self) -> bool:
        print("\n>> Search for an aircraft (or hit CTRL+C to cancel)\n")

        registration = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the aircraft registration: ",
            allow_blank=True
        )        
        if registration.is_cancelled:
            return False

        result = self.__aircraft_service.search_aircraft("registration", registration.value)

        if len(result) == 0:
            print("\n     No matching results.")
        else:
            print(f"\n     {len(result)} match(es) found:\n")
            print(self.__aircraft_service.get_results_view(result))

        return True

    def __add_option(self) -> bool:
        print("\n>> Add an aircraft (or hit CTRL+C to cancel)\n")

        # Prompt the user to complete fields
        new = self.__prompt_add_aircraft()
        if new is None: # Process was cancelled by the user
            return False

        try:
            self.__aircraft_service.add_aircraft(new)
            print("\nNew record successfully added.\n")
        except:
            print("\nError adding aircraft.\n")
        
        return True

    def __update_option(self) -> bool:
        print("\n>> Update an aircraft (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to edit
        aircraft = self.__get_aircraft_from_selection()
        if aircraft is None or aircraft.id is None:
            return False

        print(f"\nEditing information (aircraft ID {aircraft.id})\n")

        # Prompt the user to edit fields
        update = self.__prompt_update_aircraft(aircraft)
        if update is None: # Process was cancelled by the user
            return False

        # Update the aircraft record
        try:
            self.__aircraft_service.update_aircraft(update)
            print("\nRecord successfully updated.\n")
        except:
            print("\nError updating aircraft.\n")

        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete an aircraft (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to delete
        aircraft = self.__prompt_delete_aircraft()
        if aircraft is None:
            return False
        
        # Delete the aircraft
        try:
            self.__aircraft_service.delete_aircraft(aircraft)
            print("\nRecord successfully deleted.\n")
        except:
            print("\nError deleting aircraft.\n")
        
        return True

    def __prompt_add_aircraft(self) -> Aircraft | None:

        registration = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the aircraft registration: ",
            allow_blank=False
        )        
        if registration.is_cancelled:
            return None

        manufacturer_serial_no = UserPrompt(
            session=self.__session,
            prompt_type="integer",
            prompt="Enter the manufacturer serial number: ",
            allow_blank=True
        )        
        if manufacturer_serial_no.is_cancelled:
            return None

        icao_hex = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the ICAO hex code: ",
            allow_blank=True
        )        
        if icao_hex.is_cancelled:
            return None

        manufacturer = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the manufacturer: ",
            allow_blank=False
        )        
        if manufacturer.is_cancelled:
            return None

        model = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the model: ",
            allow_blank=False
        )        
        if model.is_cancelled:
            return None

        icao_type = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the ICAO type: ",
            allow_blank=True
        )        
        if icao_type.is_cancelled:
            return None
        print()

        status = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select an aircraft status:\n",
            options=[
                ("Active", ("Active")),
                ("Inactive", ("Inactive")),
                ("Retired", ("Retired"))
            ],
            key_bindings=self.__bindings
        )
        if status.is_cancelled:
            return None
        print()

        return Aircraft(
            registration=registration.value,
            manufacturer_serial_no=int(manufacturer_serial_no.value)
            if manufacturer_serial_no.value is not None else None,
            icao_hex=icao_hex.value,
            manufacturer=manufacturer.value,
            model=model.value,
            icao_type=icao_type.value,
            status=status.value
        )

    def __prompt_update_aircraft(self, aircraft: Aircraft) -> Aircraft | None:
        
        registration = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the aircraft registration: ",
            allow_blank=False,
            default_value=aircraft.registration
        )        
        if registration.is_cancelled:
            return None

        manufacturer_serial_no = UserPrompt(
            session=self.__session,
            prompt_type="integer",
            prompt="Enter the manufacturer serial number: ",
            allow_blank=True,
            default_value=aircraft.manufacturer_serial_no
        )        
        if manufacturer_serial_no.is_cancelled:
            return None

        icao_hex = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the ICAO hex code: ",
            allow_blank=True,
            default_value=aircraft.icao_hex
        )        
        if icao_hex.is_cancelled:
            return None

        manufacturer = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the manufacturer: ",
            allow_blank=False,
            default_value=aircraft.manufacturer
        )        
        if manufacturer.is_cancelled:
            return None

        model = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the model: ",
            allow_blank=False,
            default_value=aircraft.model
        )        
        if model.is_cancelled:
            return None

        icao_type = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the ICAO type: ",
            allow_blank=True,
            default_value=aircraft.icao_type
        )        
        if icao_type.is_cancelled:
            return None
        print()

        status = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select an aircraft status:\n",
            options=[
                ("Active", ("Active")),
                ("Inactive", ("Inactive")),
                ("Retired", ("Retired"))
            ],
            default_value=aircraft.status,
            key_bindings=self.__bindings
        )
        if status.is_cancelled:
            return None
        print()

        return Aircraft(
            id=aircraft.id,
            registration=registration.value,
            manufacturer_serial_no=int(manufacturer_serial_no.value)
            if manufacturer_serial_no.value is not None else None,
            icao_hex=icao_hex.value,
            manufacturer=manufacturer.value,
            model=model.value,
            icao_type=icao_type.value,
            status=status.value
        )
    
    def __prompt_delete_aircraft(self) -> Aircraft | None:

        # Prompt for the aircraft to delete
        aircraft = self.__get_aircraft_from_selection()
        if aircraft is None or aircraft.id is None:
            return None
        
        # Prompt for confirmation and delete if confirmed
        confirm = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Are you sure you want to delete this record?\n",
            options=[(1, "yes"),(0, "no")],
            key_bindings=self.__bindings
        )

        if confirm.is_cancelled or confirm.value == False:
            return None
        
        return aircraft

    def __get_aircraft_from_selection(self) -> Aircraft | None:
        aircraft_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Choose an aircraft to update:\n",
            options=self.__aircraft_service.get_aircraft_choices(),
            key_bindings=self.__bindings
        )
        if aircraft_id.is_cancelled:
            return None

        return self.__aircraft_service.get_aircraft_by_id(int(aircraft_id.value))