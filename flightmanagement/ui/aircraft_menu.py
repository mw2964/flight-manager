from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel
from flightmanagement.services.aircraft_service import AircraftService

class AircraftMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__aircraft_service = AircraftService()
        self.__session = session
        self.__bindings = bindings

    def load(self):

        while True:

            menu_title = "\nAircraft menu"
            menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

            __menu_options = [
                ("show", "Show all aircraft"),
                ("search", "Search aircraft"),
                ("add", "Add an aircraft"),
                ("update", "Update an aircraft"),
                ("delete", "Remove an aircraft"),
                ("back", "Back to main menu")
            ]

            __choose_menu = choice(
                message=menu_title,
                options=__menu_options
            )

            if __choose_menu == "show":

                print("\n>> Displaying all aircraft\n")
                print(self.__aircraft_service.get_aircraft_list())

            elif __choose_menu == "search":

                print("\n>> Search for an aircraft (or hit CTRL+C to cancel)\n")
                registration = prompt_or_cancel(self.__session, "Enter an aircraft registration: ", "Search cancelled.")
                if registration is None:
                    continue
                result = self.__aircraft_service.search_aircraft("registration", registration)
                print(result)

            elif __choose_menu == "add":

                print("\n>> Add an aircraft (or hit CTRL+C to cancel)\n")

                registration = prompt_or_cancel(self.__session, "Enter the aircraft registration: ", "Action cancelled.")
                
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

                icao_hex = prompt_or_cancel(self.__session, "Enter the ICAO hex code: ", "Action cancelled.")
                manufacturer = prompt_or_cancel(self.__session, "Enter the manufacturer: ", "Action cancelled.")
                model = prompt_or_cancel(self.__session, "Enter the model: ", "Action cancelled.")
                icao_type = prompt_or_cancel(self.__session, "Enter the ICAO type: ", "Action cancelled.")
                status = prompt_or_cancel(self.__session, "Enter the aircraft status: ", "Action cancelled.")

                if registration is None or manufacturer_serial_no is None or icao_hex is None or manufacturer is None or model is None or icao_type is None or status is None:
                    continue

                print()
                self.__aircraft_service.add_aircraft(registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)

            elif __choose_menu == "update":

                print("\n>> Update an aircraft (or hit CTRL+C to cancel)\n")

                id = choice(
                    message="Choose an aircraft to update: ",
                    options=self.__aircraft_service.get_aircraft_choices(),
                    key_bindings=self.__bindings
                )

                # Retrieve the aricraft record
                aircraft = self.__aircraft_service.get_aircraft_by_id(id)

                if aircraft:

                    print(f"\nEditing information (aircraft ID {id})\n")

                    registration = prompt_or_cancel(self.__session, "Registration: ", "Update cancelled", aircraft.registration)
                    
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
                    
                    icao_hex = prompt_or_cancel(self.__session, "ICAO hex code: ", "Update cancelled.", aircraft.icao_hex)
                    manufacturer = prompt_or_cancel(self.__session, "Manufacturer: ", "Update cancelled.", aircraft.manufacturer)
                    model = prompt_or_cancel(self.__session, "Model: ", "Update cancelled.", aircraft.model)
                    icao_type = prompt_or_cancel(self.__session, "ICAO type: ", "Update cancelled.", aircraft.icao_type)
                    
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
                    
                    if registration is None or manufacturer_serial_no is None or icao_hex is None or manufacturer is None or model is None or icao_type is None or status is None:
                        continue
                    
                    print()
                    self.__aircraft_service.update_aircraft(id, registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)

            elif __choose_menu == "delete":

                print("\n>> Delete an aircraft (or hit CTRL+C to cancel)\n")

                id = choice(
                    message="Choose an aircraft to delete: ",
                    options=self.__aircraft_service.get_aircraft_choices(),
                    key_bindings=self.__bindings
                )

                print()
                if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
                    print()
                    self.__aircraft_service.delete_aircraft(id)
                else:
                    print("\nDelete cancelled.")

            elif __choose_menu == "back":
                break
            else:
                print("Invalid choice")