from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel, prompt_date, prompt_time
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.airport_service import AirportService
from flightmanagement.services.pilot_service import PilotService

class FlightMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__flight_service = FlightService()
        self.__aircraft_service = AircraftService()
        self.__airport_service = AirportService()
        self.__pilot_service = PilotService()
        self.__session = session
        self.__bindings = bindings

    def load(self):

        while True:

            menu_title = "\nFlights menu"
            menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

            __menu_options = [
                ("show", "Show all flights"),
                ("search", "Search flights"),
                ("add", "Add a flight"),
                ("update", "Update a flight"),
                ("delete", "Remove a flight"),
                ("back", "Back to main menu")
            ]

            __choose_menu = choice(
                message=menu_title,
                options=__menu_options
            )

            if __choose_menu == "show":

                print("\n>> Displaying all flights\n")
                print(self.__flight_service.get_flight_list())

            elif __choose_menu == "search":

                print("\n>> Search for a flight (or hit CTRL+C to cancel)\n")
                
            elif __choose_menu == "add":

                print("\n>> Add a flight (or hit CTRL+C to cancel)\n")

                flight_number = prompt_or_cancel(self.__session, "Flight number: ", "Action cancelled.")
                print()

                aircraft_id = choice(
                    message="Select the aircraft: ",
                    options=self.__aircraft_service.get_aircraft_choices(),
                    key_bindings=self.__bindings
                )
                print()

                origin_id = choice(
                    message="Select the origin airport: ",
                    options=self.__airport_service.get_airport_choices(),
                    key_bindings=self.__bindings
                )
                print()

                destination_id = choice(
                    message="Select the destination airport: ",
                    options=self.__airport_service.get_airport_choices(),
                    key_bindings=self.__bindings
                )
                print()

                pilot_id = choice(
                    message="Select the pilot: ",
                    options=self.__pilot_service.get_pilot_choices(),
                    key_bindings=self.__bindings
                )
                print()

                copilot_id = choice(
                    message="Select the copilot: ",
                    options=self.__pilot_service.get_pilot_choices(),
                    key_bindings=self.__bindings
                )
                print()

                while True:
                        try:
                            departure_date = prompt_date(self.__session, "Scheduled departure date (dd/mm/yyyy): ", True)
                            break
                        except ValueError:
                            print("\tInvalid date - please try again.")

                while True:
                    try:
                        departure_time = prompt_time(self.__session, "Scheduled departure time (HH:MM): ", True)
                        break
                    except ValueError:
                        print("\tInvalid time - please try again.")

                while True:
                        try:
                            arrival_date = prompt_date(self.__session, "Scheduled arrival date (dd/mm/yyyy): ", True, departure_date)
                            break
                        except ValueError:
                            print("\tInvalid date - please try again.")

                while True:
                    try:
                        arrival_time = prompt_time(self.__session, "Scheduled arrival time (HH:MM): ", True)
                        break
                    except ValueError:
                        print("\tInvalid time - please try again.")

                # Handle if the user has cancelled on any of these prompts
                if flight_number is None or departure_date is None or departure_time is None or arrival_date is None or arrival_time is None:
                    continue

                self.__flight_service.add_flight(flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_date, departure_time, arrival_date, arrival_time)

            elif __choose_menu == "update":

                print("\n>> Update a flight (or hit CTRL+C to cancel)\n")

                flight_no_search = prompt_or_cancel(self.__session, "Enter a flight number (or leave blank to select from all flights): ", "Update cancelled.")
                if flight_no_search is None:
                    continue
                
                print()

                id = choice(
                    message="Select the flight to update: ",
                    options=self.__flight_service.get_flight_choices(flight_no_search),
                    key_bindings=self.__bindings
                )
                
                # Retrieve the flight record
                flight = self.__flight_service.get_flight(id)

                print(f"\nEditing information (flight ID {id})\n")

                if flight:

                    while True:
                        flight_number = prompt_or_cancel("Flight number: ", "Update cancelled.", flight.flight_number)
                        if flight_number:
                            break
                        else:
                            print("Flight number cannot be blank.")
                    print()
                    
                    aircraft_id = choice(
                        message="Select an aircraft: ",
                        options=self.__aircraft_service.get_aircraft_choices(),
                        default=flight.aircraft_id,
                        key_bindings=self.__bindings
                    )
                    print()
                
                    origin_id = choice(
                        message="Select an origin airport: ",
                        options=self.__airport_service.get_airport_choices(),
                        default=flight.origin_id,
                        key_bindings=self.__bindings
                    )
                    print()
                            
                    destination_id = choice(
                        message="Select a destination airport: ",
                        options=self.__airport_service.get_airport_choices(),
                        default=flight.destination_id,
                        key_bindings=self.__bindings
                    )
                    print()

                    pilot_id = choice(
                        message="Select a pilot: ",
                        options=self.__pilot_service.get_pilot_choices(),
                        default=flight.pilot_id,
                        key_bindings=self.__bindings
                    )
                    print()

                    copilot_id = choice(
                        message="Select a copilot: ",
                        options=self.__pilot_service.get_pilot_choices(),
                        default=flight.copilot_id,
                        key_bindings=self.__bindings
                    )
                    print()

                    while True:
                        try:
                            default = ""
                            if flight.departure_time_scheduled:
                                default = datetime.strftime(flight.departure_time_scheduled, "%d/%m/%Y")
                            departure_date_scheduled = prompt_date(self.__session, "Scheduled departure date (dd/mm/yyyy): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid date - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.departure_time_scheduled:
                                default = datetime.strftime(flight.departure_time_scheduled, "%H:%M")
                            departure_time_scheduled = prompt_time(self.__session, "Scheduled departure time (HH:MM): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid time - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.arrival_time_scheduled:
                                default = datetime.strftime(flight.arrival_time_scheduled, "%d/%m/%Y")
                            arrival_date_scheduled = prompt_date(self.__session, "Scheduled arrival date (dd/mm/yyyy): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid date - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.arrival_time_scheduled:
                                default = datetime.strftime(flight.arrival_time_scheduled, "%H:%M")
                            arrival_time_scheduled = prompt_time(self.__session, "Scheduled arrival time (HH:MM): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid time - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.departure_time_actual:
                                default = datetime.strftime(flight.departure_time_actual, "%d/%m/%Y")
                            departure_date_actual = prompt_date(self.__session, "Actual departure date (dd/mm/yyyy): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid date - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.departure_time_actual:
                                default = datetime.strftime(flight.departure_time_actual, "%H:%M")
                            departure_time_actual = prompt_time(self.__session, "Actual departure time (HH:MM): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid time - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.arrival_time_actual:
                                default = datetime.strftime(flight.arrival_time_actual, "%d/%m/%Y")
                            arrival_date_actual = prompt_date(self.__session, "Actual arrival date (dd/mm/yyyy): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid date - please try again.")

                    while True:
                        try:
                            default = ""
                            if flight.arrival_time_actual:
                                default = datetime.strftime(flight.arrival_time_actual, "%H:%M")
                            arrival_time_actual = prompt_time(self.__session, "Actual arrival time (HH:MM): ", True, default)
                            break
                        except ValueError:
                            print("\tInvalid time - please try again.")

                    status = choice(
                        message="Select a flight status: ",
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
                    print()

                    # Handle if the user has cancelled on any of these prompts
                    if flight_number is None or departure_date_scheduled is None or departure_time_scheduled is None or arrival_date_scheduled is None or arrival_time_scheduled is None or departure_date_actual is None or departure_time_actual is None or arrival_date_actual is None or arrival_time_actual is None:
                        continue

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

            elif __choose_menu == "delete":

                print("\n-- REMOVE A FLIGHT --\n")
                __id = int(input("Enter the ID of the flight that you would like to delete: "))
                self.__flight_service.delete_flight(__id)

            elif __choose_menu == "back":
                break
            else:
                print("Invalid Choice")