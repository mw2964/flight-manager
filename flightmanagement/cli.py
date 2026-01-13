from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import choice, clear
from prompt_toolkit.key_binding import KeyBindings
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.airport_service import AirportService
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.services.admin_service import AdminService
from flightmanagement.services.report_service import ReportService
from flightmanagement.utils.utils import indent_string

__flight_service = FlightService()
__aircraft_service = AircraftService()
__airport_service = AirportService()
__pilot_service = PilotService()
__admin_service = AdminService()
__report_service = ReportService()

CANCEL = "__CANCEL__"

bindings = KeyBindings()

@bindings.add('c-c')
def _(event):
    event.app.exit(result=CANCEL)            

session = PromptSession(key_bindings=bindings)

def prompt_or_cancel(message: str, cancel_message: str, default_value = None):
    
    indented_message = indent_string(message, 5)

    if default_value:
        result = session.prompt(
            message=indented_message,
            default=default_value
        )
    else:
        result = session.prompt(
            message=indented_message
        )

    if result == CANCEL:
        print(f"\n{cancel_message}")
        return None
    return result

def main_menu():
    while True:
        menu_title = "\nMain menu"
        menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

        __menu_options = [
            ("flights", "Flights"),
            ("pilots", "Pilots"),
            ("airports", "Airports"),
            ("aircraft", "Aircraft"),
            ("reports", "Reports"),
            ("admin", "Admin"),
            ("exit", "Exit")
        ]

        __choose_menu = choice(
            message=menu_title,
            options=__menu_options
        )

        if __choose_menu == "flights":
            flights_menu()
        elif __choose_menu == "pilots":
            pilots_menu()
        elif __choose_menu == "airports":
            airports_menu()
        elif __choose_menu == "aircraft":
            aircraft_menu()
        elif __choose_menu == "reports":
            reports_menu()
        elif __choose_menu == "admin":
            admin_menu()
        elif __choose_menu == "exit":
            exit(0)
        else:
            print("Invalid Choice")


def flights_menu():
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
            print(__flight_service.get_flight_list())

        elif __choose_menu == "search":

            print("\n>> Search for a flight (or hit CTRL+C to cancel)\n")
            
        elif __choose_menu == "add":

            print("\n>> Add a flight (or hit CTRL+C to cancel)\n")

            flight_number = prompt_or_cancel("Flight number: ", "Action cancelled.")
            print()

            aircraft_id = choice(
                message="Select the aircraft: ",
                options=__aircraft_service.get_aircraft_choices(),
                key_bindings=bindings
            )
            print()

            origin_id = choice(
                message="Select the origin airport: ",
                options=__airport_service.get_airport_choices(),
                key_bindings=bindings
            )
            print()

            destination_id = choice(
                message="Select the destination airport: ",
                options=__airport_service.get_airport_choices(),
                key_bindings=bindings
            )
            print()

            pilot_id = choice(
                message="Select the pilot: ",
                options=__pilot_service.get_pilot_choices(),
                key_bindings=bindings
            )
            print()

            copilot_id = choice(
                message="Select the copilot: ",
                options=__pilot_service.get_pilot_choices(),
                key_bindings=bindings
            )
            print()

            while True:
                    try:
                        departure_date = prompt_date("Scheduled departure date (dd/mm/yyyy): ", True)
                        break
                    except ValueError:
                        print("\tInvalid date - please try again.")

            while True:
                try:
                    departure_time = prompt_time("Scheduled departure time (HH:MM): ", True)
                    break
                except ValueError:
                    print("\tInvalid time - please try again.")

            while True:
                    try:
                        arrival_date = prompt_date("Scheduled arrival date (dd/mm/yyyy): ", True, departure_date)
                        break
                    except ValueError:
                        print("\tInvalid date - please try again.")

            while True:
                try:
                    arrival_time = prompt_time("Scheduled arrival time (HH:MM): ", True)
                    break
                except ValueError:
                    print("\tInvalid time - please try again.")

            # Handle if the user has cancelled on any of these prompts
            if flight_number is None or departure_date is None or departure_time is None or arrival_date is None or arrival_time is None:
                continue

            __flight_service.add_flight(flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_date, departure_time, arrival_date, arrival_time)

        elif __choose_menu == "update":

            print("\n>> Update a flight (or hit CTRL+C to cancel)\n")

            flight_no_search = prompt_or_cancel("Enter a flight number (or leave blank to select from all flights): ", "Update cancelled.")
            if flight_no_search is None:
                continue
            
            print()

            id = choice(
                message="Select the flight to update: ",
                options=__flight_service.get_flight_choices(flight_no_search),
                key_bindings=bindings
            )
            
            # Retrieve the flight record
            flight = __flight_service.get_flight(id)

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
                    options=__aircraft_service.get_aircraft_choices(),
                    default=flight.aircraft_id,
                    key_bindings=bindings
                )
                print()
            
                origin_id = choice(
                    message="Select an origin airport: ",
                    options=__airport_service.get_airport_choices(),
                    default=flight.origin_id,
                    key_bindings=bindings
                )
                print()
                        
                destination_id = choice(
                    message="Select a destination airport: ",
                    options=__airport_service.get_airport_choices(),
                    default=flight.destination_id,
                    key_bindings=bindings
                )
                print()

                pilot_id = choice(
                    message="Select a pilot: ",
                    options=__pilot_service.get_pilot_choices(),
                    default=flight.pilot_id,
                    key_bindings=bindings
                )
                print()

                copilot_id = choice(
                    message="Select a copilot: ",
                    options=__pilot_service.get_pilot_choices(),
                    default=flight.copilot_id,
                    key_bindings=bindings
                )
                print()

                while True:
                    try:
                        default = ""
                        if flight.departure_time_scheduled:
                            default = datetime.strftime(flight.departure_time_scheduled, "%d/%m/%Y")
                        departure_date_scheduled = prompt_date("Scheduled departure date (dd/mm/yyyy): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid date - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.departure_time_scheduled:
                            default = datetime.strftime(flight.departure_time_scheduled, "%H:%M")
                        departure_time_scheduled = prompt_time("Scheduled departure time (HH:MM): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid time - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.arrival_time_scheduled:
                            default = datetime.strftime(flight.arrival_time_scheduled, "%d/%m/%Y")
                        arrival_date_scheduled = prompt_date("Scheduled arrival date (dd/mm/yyyy): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid date - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.arrival_time_scheduled:
                            default = datetime.strftime(flight.arrival_time_scheduled, "%H:%M")
                        arrival_time_scheduled = prompt_time("Scheduled arrival time (HH:MM): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid time - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.departure_time_actual:
                            default = datetime.strftime(flight.departure_time_actual, "%d/%m/%Y")
                        departure_date_actual = prompt_date("Actual departure date (dd/mm/yyyy): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid date - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.departure_time_actual:
                            default = datetime.strftime(flight.departure_time_actual, "%H:%M")
                        departure_time_actual = prompt_time("Actual departure time (HH:MM): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid time - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.arrival_time_actual:
                            default = datetime.strftime(flight.arrival_time_actual, "%d/%m/%Y")
                        arrival_date_actual = prompt_date("Actual arrival date (dd/mm/yyyy): ", True, default)
                        break
                    except ValueError:
                        print("\tInvalid date - please try again.")

                while True:
                    try:
                        default = ""
                        if flight.arrival_time_actual:
                            default = datetime.strftime(flight.arrival_time_actual, "%H:%M")
                        arrival_time_actual = prompt_time("Actual arrival time (HH:MM): ", True, default)
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
                    key_bindings=bindings
                )
                print()

                # Handle if the user has cancelled on any of these prompts
                if flight_number is None or departure_date_scheduled is None or departure_time_scheduled is None or arrival_date_scheduled is None or arrival_time_scheduled is None or departure_date_actual is None or departure_time_actual is None or arrival_date_actual is None or arrival_time_actual is None:
                    continue

                __flight_service.update_flight(
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
            __flight_service.delete_flight(__id)

        elif __choose_menu == "back":
            break
        else:
            print("Invalid Choice")

def prompt_date(prompt: str, allow_blank: bool, default=None) -> str | None:

    if default:
        value = prompt_or_cancel(prompt, "Update cancelled", default)
    else:
        value = prompt_or_cancel(prompt, "Update cancelled")

    if not value:
        if allow_blank:
            return None        
        raise ValueError("Invalid date")

    try:
        date = datetime.strptime(value, "%d/%m/%Y")
    except:
        raise ValueError("Invalid date")
    
    return datetime.strftime(date, "%Y-%m-%d")

def prompt_time(prompt: str, allow_blank: bool, default=None) -> str | None:

    if default:
        value = prompt_or_cancel(prompt, "Update cancelled", default)
    else:
        value = prompt_or_cancel(prompt, "Update cancelled")

    if not value:
        if allow_blank:
            return None        
        raise ValueError("Invalid time")

    try:
        date = datetime.strptime(value, "%H:%M")
    except:
        raise ValueError("Invalid time")
    
    return datetime.strftime(date, "%H:%M")

def pilots_menu():

    while True:

        menu_title = "\nPilots menu"
        menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

        __menu_options = [
            ("show", "Show all pilots"),
            ("search", "Search pilots"),
            ("add", "Add a pilot"),
            ("update", "Update a pilot"),
            ("delete", "Remove a pilot"),
            ("back", "Back to main menu")
        ]

        __choose_menu = choice(
            message=menu_title,
            options=__menu_options
        )

        if __choose_menu == "show":

            print("\n>> Displaying all pilots\n")
            print(__pilot_service.get_pilot_table())

        elif __choose_menu == "search":

            print("\n>> Search for a pilot (or hit CTRL+C to cancel)\n")
            family_name = prompt_or_cancel("Enter a family name: ", "Search cancelled.")
            if family_name is None:                
                continue
            result = __pilot_service.search_pilots("family_name", family_name)
            print(result)

        elif __choose_menu == "add":

            print("\n>> Add a pilot (or hit CTRL+C to cancel)\n")

            first_name = prompt_or_cancel("Enter a first name: ", "Action cancelled.")
            family_name = prompt_or_cancel("Enter a family name: ", "Action cancelled.")

            if first_name is None or family_name is None:
                continue

            __pilot_service.add_pilot(first_name, family_name)

        elif __choose_menu == "update":

            print("\n>> Update a pilot (or hit CTRL+C to cancel)\n")

            id = choice(
                message="Choose a pilot to update: ",
                options=__pilot_service.get_pilot_choices(),
                key_bindings=bindings
            )

            # Retrieve the pilot record
            pilot = __pilot_service.get_pilot_by_id(id)

            if pilot:

                print(f"\nEditing information (pilot ID {id})\n")

                first_name = prompt_or_cancel("First name: ", "Update cancelled", pilot.first_name)
                family_name = prompt_or_cancel("Family name: ", "Update cancelled", pilot.family_name)

                if first_name is None or family_name is None:
                    continue

                print()
                __pilot_service.update_pilot(id, first_name, family_name)

        elif __choose_menu == "delete":

            print("\n>> Delete a pilot (or hit CTRL+C to cancel)\n")

            id = choice(
                message="Choose a pilot to delete: ",
                options=__pilot_service.get_pilot_choices(),
                key_bindings=bindings
            )

            # Retrieve the pilot record
            pilot = __pilot_service.get_pilot_by_id(id)

            if pilot:
                print()
                if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
                    print()
                    __pilot_service.delete_pilot(id)
                else:
                    print("\nDelete cancelled.")

        elif __choose_menu == "back":
            return
        else:
            print("Invalid Choice")


def airports_menu():
    while True:

        menu_title = "\nAirports menu"
        menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

        __menu_options = [
            ("show", "Show all airports"),
            ("search", "Search airports"),
            ("add", "Add an airport"),
            ("update", "Update an airport"),
            ("delete", "Remove an airport"),
            ("back", "Back to main menu")
        ]

        __choose_menu = choice(
            message=menu_title,
            options=__menu_options
        )

        if __choose_menu == "show":

            print("\n-- SHOW ALL AIRPORTS --\n")
            print(__airport_service.get_airport_list())

        elif __choose_menu == "search":

            print("\n-- SEARCH AIRPORTS --\n")
            __code = input("Enter an airport code: ")
            result = __airport_service.search_airports("code", __code)
            print(result)

        elif __choose_menu == "add":

            print("\n-- ADD AN AIRPORT --\n")
            __code = input("Enter the airport code: ")
            __name = input("Enter the airport name: ")
            __city = input("Enter the city: ")
            __country = input("Enter the country: ")
            __region = input("Enter the region: ")
            __airport_service.add_airport(__code, __name, __city, __country, __region)

        elif __choose_menu == "update":

            print("\n-- UPDATE AN AIRPORT --\n")
            __id = int(input("Enter the ID of the airport that you would like to update: "))
            __code = input("Enter a new code (or leave blank to skip): ")
            __name = input("Enter a new name (or leave blank to skip): ")
            __city = input("Enter a new city (or leave blank to skip): ")
            __country = input("Enter a new country (or leave blank to skip): ")
            __region = input("Enter a new region (or leave blank to skip): ")
            __airport_service.update_airport(__id, __code, __name, __city, __country, __region)

        elif __choose_menu == "delete":

            print("\n-- REMOVE AN AIRPORT --\n")
            __id = int(input("Enter the ID of the airport that you would like to delete: "))
            __airport_service.delete_airport(__id)

        elif __choose_menu == "back":
            break
        else:
            print("Invalid Choice")

def aircraft_menu():
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

            print("\n-- SHOW ALL AIRCRAFT --\n")
            print(__aircraft_service.get_aircraft_list())

        elif __choose_menu == "search":

            print("\n-- SEARCH AIRCRAFT --\n")
            __registration = input("Enter a registration: ")
            result = __aircraft_service.search_aircraft("registration", __registration)
            print(result)

        elif __choose_menu == "add":

            print("\n-- ADD AN AIRCRAFT --\n")
            __registration = input("Enter the aircraft registration: ")
            __manufacturer_serial_no = int(input("Enter the manufacturer serial number: "))
            __icao_hex = input("Enter the ICAO hex code: ")
            __manufacturer = input("Enter the manufacturer: ")
            __model = input("Enter the model: ")
            __icao_type = input("Enter the ICAO type: ")
            __status = input("Enter the aircraft status: ")
            __aircraft_service.add_aircraft(__registration, __manufacturer_serial_no, __icao_hex, __manufacturer, __model, __icao_type, __status)

        elif __choose_menu == "update":

            print("\n-- UPDATE AN AIRCRAFT --\n")
            __id = int(input("Enter the ID of the aircraft that you would like to update: "))
            __registration = input("Enter a new registration (or leave blank to skip): ")
            __manufacturer_serial_no = int(input("Enter a new manufacturer serial number (or leave blank to skip): "))
            __icao_hex = input("Enter a new ICAO hex code (or leave blank to skip): ")
            __manufacturer = input("Enter a new manufacturer (or leave blank to skip): ")
            __model = input("Enter a new model (or leave blank to skip): ")
            __icao_type = input("Enter a new ICAO type (or leave blank to skip): ")
            __status = input("Enter a new status (or leave blank to skip): ")
            __aircraft_service.update_aircraft(__id, __registration, __manufacturer_serial_no, __icao_hex, __manufacturer, __model, __icao_type, __status)

        elif __choose_menu == "delete":

            print("\n-- REMOVE AN AIRCRAFT --\n")
            __id = int(input("Enter the ID of the aircraft that you would like to delete: "))
            __aircraft_service.delete_aircraft(__id)

        elif __choose_menu == "back":
            break
        else:
            print("Invalid Choice")

def reports_menu():
    while True:

        menu_title = "\nReports menu"
        menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

        __menu_options = [
            ("pilot_stats", "Pilot statistics"),
            ("back", "Back to main menu")
        ]

        __choose_menu = choice(
            message=menu_title,
            options=__menu_options
        )

        if __choose_menu == "pilot_stats":

            pass

        elif __choose_menu == "back":
            break
        else:
            print("Invalid Choice")

def admin_menu():
    while True:

        menu_title = "\nAdmin menu"
        menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

        __menu_options = [
            ("init_db", "Initialise database"),
            ("back", "Back to main menu")
        ]

        __choose_menu = choice(
            message=menu_title,
            options=__menu_options
        )

        if __choose_menu == "init_db":

            __admin_service.initialise_database()
            
        elif __choose_menu == "back":
            break
        else:
            print("Invalid Choice")

print("\nFLIGHT CLUB\nV0.1")
main_menu()