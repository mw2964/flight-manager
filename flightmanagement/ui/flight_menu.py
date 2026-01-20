from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel, prompt_date, prompt_time, format_title
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.airport_service import AirportService
from flightmanagement.services.pilot_service import PilotService

class FlightMenu:

    __MENU_NAME = "Flights menu"
    __MENU_OPTIONS = [
        ("show", "Show all flights"),
        ("search", "Search flights"),
        ("add", "Add a flight"),
        ("update", "Update a flight"),
        ("delete", "Remove a flight"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn):
        self.__flight_service = FlightService(conn)
        self.__aircraft_service = AircraftService(conn)
        self.__airport_service = AirportService(conn)
        self.__pilot_service = PilotService(conn)
        self.__session = session
        self.__bindings = bindings

    def __show_option(self) -> None:
        print("\n>> Displaying all flights\n")
        print(self.__flight_service.get_flight_table())

    def __search_option(self) -> bool:
        print("\n>> Search for a flight (or hit CTRL+C to cancel)\n")

        flight_number = prompt_or_cancel(self.__session, "Enter flight number: ", "Search cancelled.")
        if flight_number is None:
            return False

        result = self.__flight_service.search_flights("flight_number", flight_number)

        if result is None:
            print("\n     No matching results.")
            return True

        match_count = len(result)
        if match_count == 1:
            print(f"\n     {len(result)} match found:\n")
        else:            
            print(f"\n     {len(result)} matches found:\n")

        print(self.__flight_service.get_results_view(result))
        return True

    def __add_option(self) -> bool:
        print("\n>> Add a flight (or hit CTRL+C to cancel)\n")

        flight_number = prompt_or_cancel(self.__session, "Flight number: ", "Action cancelled.")
        if flight_number is None:
            return False
        print()

        aircraft_id = choice(
            message="Select the aircraft:\n",
            options=self.__aircraft_service.get_aircraft_choices(),
            key_bindings=self.__bindings
        )
        if aircraft_id == "__CANCEL__":
            return False
        print()

        origin_id = choice(
            message="Select the origin airport:\n",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if origin_id == "__CANCEL__":
            return False
        print()

        destination_id = choice(
            message="Select the destination airport:\n",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if destination_id == "__CANCEL__":
            return False
        print()

        pilot_id = choice(
            message="Select the pilot:\n",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if pilot_id == "__CANCEL__":
            return False
        print()

        copilot_id = choice(
            message="Select the copilot:\n",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if copilot_id == "__CANCEL__":
            return False
        print()

        while True:
            try:
                departure_date = prompt_date(self.__session, "Scheduled departure date (DD/MM/YYYY): ", False)
                break
            except ValueError:
                print("\tInvalid date - please try again.")
        if departure_date is None:
            return False

        while True:
            try:
                departure_time = prompt_time(self.__session, "Scheduled departure time (HH:MM): ", False)
                break
            except ValueError:
                print("\tInvalid time - please try again.")
        if departure_time is None:
            return False

        while True:
                try:
                    if departure_date == '':
                        default = ''
                    else:
                        default = datetime.strftime(datetime.strptime(departure_date, "%Y-%m-%d"), "%d/%m/%Y")
                    arrival_date = prompt_date(self.__session, "Scheduled arrival date (DD/MM/YYY): ", False, default)
                    break
                except ValueError:
                    print("\tInvalid date - please try again.")
        if arrival_date is None:
            return False

        while True:
            try:
                arrival_time = prompt_time(self.__session, "Scheduled arrival time (HH:MM): ", False)
                break
            except ValueError:
                print("\tInvalid time - please try again.")
        if arrival_time is None:
            return False
        print()

        self.__flight_service.add_flight(flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_date, departure_time, arrival_date, arrival_time)
        return True

    def __update_option(self) -> bool:
        print("\n>> Update a flight (or hit CTRL+C to cancel)\n")

        flight_no_search = prompt_or_cancel(self.__session, "Enter a flight number (or leave blank to select from all flights): ", "Update cancelled.")
        if flight_no_search is None:
            return False
        
        print()

        id = choice(
            message="Select the flight to update:\n",
            options=self.__flight_service.get_flight_choices(flight_no_search),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            return False
        
        # Retrieve the flight record
        flight = self.__flight_service.get_flight_by_id(id)

        print(f"\nEditing information (flight ID {id})\n")

        if flight:

            while True:
                flight_number = prompt_or_cancel(self.__session, "Flight number: ", "Update cancelled.", flight.flight_number)
                if flight_number:
                    break
                else:
                    print("Flight number cannot be blank.")
            if flight_number is None:
                return False
            print()
            
            aircraft_id = choice(
                message="Select an aircraft:\n",
                options=self.__aircraft_service.get_aircraft_choices(),
                default=flight.aircraft_id,
                key_bindings=self.__bindings
            )
            if aircraft_id == "__CANCEL__":
                return False
            print()
        
            origin_id = choice(
                message="Select an origin airport:\n",
                options=self.__airport_service.get_airport_choices(),
                default=flight.origin_id,
                key_bindings=self.__bindings
            )
            if origin_id == "__CANCEL__":
                return False
            print()
                    
            destination_id = choice(
                message="Select a destination airport:\n",
                options=self.__airport_service.get_airport_choices(),
                default=flight.destination_id,
                key_bindings=self.__bindings
            )
            if destination_id == "__CANCEL__":
                return False
            print()

            pilot_id = choice(
                message="Select a pilot:\n",
                options=self.__pilot_service.get_pilot_choices(),
                default=flight.pilot_id,
                key_bindings=self.__bindings
            )
            if pilot_id == "__CANCEL__":
                return False
            print()

            copilot_id = choice(
                message="Select a copilot:\n",
                options=self.__pilot_service.get_pilot_choices(),
                default=flight.copilot_id,
                key_bindings=self.__bindings
            )
            if copilot_id == "__CANCEL__":
                return False
            print()

            while True:
                try:
                    default = ""
                    if flight.departure_time_scheduled:
                        default = datetime.strftime(flight.departure_time_scheduled, "%d/%m/%Y")
                    departure_date_scheduled = prompt_date(self.__session, "Scheduled departure date (DD/MM/YYY): ", False, default)
                    break
                except ValueError:
                    print("\tInvalid date - please try again.")
            if departure_date_scheduled is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.departure_time_scheduled:
                        default = datetime.strftime(flight.departure_time_scheduled, "%H:%M")
                    departure_time_scheduled = prompt_time(self.__session, "Scheduled departure time (HH:MM): ", False, default)
                    break
                except ValueError:
                    print("\tInvalid time - please try again.")
            if departure_time_scheduled is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.arrival_time_scheduled:
                        default = datetime.strftime(flight.arrival_time_scheduled, "%d/%m/%Y")
                    arrival_date_scheduled = prompt_date(self.__session, "Scheduled arrival date (DD/MM/YYY): ", True, default)
                    break
                except ValueError:
                    print("\tInvalid date - please try again.")
            if arrival_date_scheduled is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.arrival_time_scheduled:
                        default = datetime.strftime(flight.arrival_time_scheduled, "%H:%M")
                    arrival_time_scheduled = prompt_time(self.__session, "Scheduled arrival time (HH:MM): ", True, default)
                    break
                except ValueError:
                    print("\tInvalid time - please try again.")
            if arrival_time_scheduled is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.departure_time_actual:
                        default = datetime.strftime(flight.departure_time_actual, "%d/%m/%Y")
                    departure_date_actual = prompt_date(self.__session, "Actual departure date (DD/MM/YYY): ", True, default)
                    break # TODO CANCEL is returning '' instead of None so not working!
                except ValueError:
                    print("\tInvalid date - please try again.")
            if departure_date_actual is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.departure_time_actual:
                        default = datetime.strftime(flight.departure_time_actual, "%H:%M")
                    departure_time_actual = prompt_time(self.__session, "Actual departure time (HH:MM): ", True, default)
                    break
                except ValueError:
                    print("\tInvalid time - please try again.")
            if departure_date_actual is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.arrival_time_actual:
                        default = datetime.strftime(flight.arrival_time_actual, "%d/%m/%Y")
                    arrival_date_actual = prompt_date(self.__session, "Actual arrival date (DD/MM/YYY): ", True, default)
                    break
                except ValueError:
                    print("\tInvalid date - please try again.")
            if arrival_date_actual is None:
                return False

            while True:
                try:
                    default = ""
                    if flight.arrival_time_actual:
                        default = datetime.strftime(flight.arrival_time_actual, "%H:%M")
                    arrival_time_actual = prompt_time(self.__session, "Actual arrival time (HH:MM): ", True, default)
                    break
                except ValueError:
                    print("\tInvalid time - please try again.")
            if arrival_time_actual is None:
                return False
            print()

            status = choice(
                message="Select a flight status:\n",
                options=[
                    ("Scheduled", ("Scheduled")),
                    ("Delayed", ("Delayed")),
                    ("On time", ("On time")),
                    ("Boarding", ("Boarding")),
                    ("Closed", ("Closed")),
                    ("Departed", ("Departed")),
                    ("Arrived", ("Arrived"))
                ],
                default=flight.status,
                key_bindings=self.__bindings
            )
            if status == "__CANCEL__":
                return False
            print()

            if arrival_date_scheduled == "":
                arrival_date_scheduled = None
            if departure_date_actual == "":
                departure_date_actual = None
            if arrival_date_actual == "":
                arrival_date_actual = None
            if arrival_time_scheduled == "":
                arrival_time_scheduled = None
            if departure_time_actual == "":
                departure_time_actual = None
            if arrival_time_actual == "":
                arrival_time_actual = None

            try:
                self.__flight_service.update_flight(
                    id,                    
                    flight_number,
                    aircraft_id,
                    origin_id,
                    destination_id,
                    pilot_id,
                    copilot_id,
                    departure_date_scheduled,
                    departure_time_scheduled,
                    arrival_date_scheduled,
                    arrival_time_scheduled,
                    departure_date_actual,
                    departure_time_actual,
                    arrival_date_actual,
                    arrival_time_actual,
                    status
                )
                print("Flight details successfully updated.")
            except ValueError as e:
                print(f"Error: {e}. Your changes could not be saved.")
        
        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete a flight (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose a flight to delete:\n",
            options=self.__flight_service.get_flight_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            return False

        print()
        if choice(message="Are you sure you want to delete this record?\n", options=[(1, "yes"),(0, "no")]) == 1:
            print()
            self.__flight_service.delete_flight(id)
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
                print("Invalid choice.")