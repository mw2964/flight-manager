from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.airport_service import AirportService
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.services.admin_service import AdminService
from flightmanagement.services.report_service import ReportService

__flight_service = FlightService()
__aircraft_service = AircraftService()
__airport_service = AirportService()
__pilot_service = PilotService()
__admin_service = AdminService()
__report_service = ReportService()

def main_menu():
    while True:
        menu_title = "Main menu"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Flights")
        print(" 2. Pilots")
        print(" 3. Airports")
        print(" 4. Aircraft")
        print(" 5. Reports")
        print(" 6. Admin")
        print(" 7. Exit")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":
            flights_menu()
        elif __choose_menu == "2":
            pilots_menu()
        elif __choose_menu == "3":
            airports_menu()
        elif __choose_menu == "4":
            aircraft_menu()
        elif __choose_menu == "5":
            reports_menu()
        elif __choose_menu == "6":
            admin_menu()
        elif __choose_menu == "7":
            exit(0)
        else:
            print("Invalid Choice")


def flights_menu():
    while True:
        menu_title = "Flights menu"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Show all flights")
        print(" 2. Search flights")
        print(" 3. Add a flight")
        print(" 4. Update a flight")
        print(" 5. Remove a flight")
        print(" 6. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            print("\n-- SHOW ALL FLIGHTS --\n")
            print(__flight_service.get_flight_list())

        elif __choose_menu == "2":

            print("\n-- SEARCH FLIGHTS --\n")
            
        elif __choose_menu == "3":

            print("\n-- ADD A FLIGHT --\n")
            __flight_number = input("Enter the flight number: ")
            
            while True:
                __aircraft = input("Enter the aircraft registration: ")
                if __aircraft_service.search_aircraft("registration", __aircraft) != "\nNo matching records":
                    break
                else:
                    print("No matching aircraft found. Please try again.")
            __origin = input("Enter the origin airport code: ")
            __destination = input("Enter the destination airport code: ")
            __pilot_id = int(input("Enter the pilot ID (see list above): "))
            __copilot_id = int(input("Enter the copilot ID (see list above): "))
            __departure_date = input("Enter the departure date (YYYY-MM-DD): ")
            __departure_time = input("Enter the departure time (HH:MM): ")
            __arrival_date = input("Enter the arrival date (YYYY-MM-DD): ")
            __arrival_time = input("Enter the arrival time (HH:MM): ")
            __flight_service.add_flight(__flight_number, __aircraft, __origin, __destination, __pilot_id, __copilot_id, __departure_date, __departure_time, __arrival_date, __arrival_time)

        elif __choose_menu == "4":

            print("\n-- UPDATE A FLIGHT --\n")

        elif __choose_menu == "5":

            print("\n-- REMOVE A FLIGHT --\n")
            __id = int(input("Enter the ID of the flight that you would like to delete: "))
            __flight_service.delete_flight(__id)

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def pilots_menu():
    while True:
        menu_title = "Pilots menu"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Show all pilots")
        print(" 2. Search pilots")
        print(" 3. Add a pilot")
        print(" 4. Update a pilot")
        print(" 5. Remove a pilot")
        print(" 6. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            print("\n-- SHOW ALL PILOTS --\n")
            print(__pilot_service.get_pilot_list())

        elif __choose_menu == "2":

            print("\n-- SEARCH PILOTS --\n")
            __family_name = input("Enter a family name: ")
            result = __pilot_service.search_pilots("family_name", __family_name)
            print(result)

        elif __choose_menu == "3":

            print("\n-- ADD A PILOT --\n")
            __first_name = input("Enter a first name: ")
            __family_name = input("Enter a family name: ")
            __pilot_service.add_pilot(__first_name, __family_name)

        elif __choose_menu == "4":

            print("\n-- UPDATE A PILOT --\n")
            __id = int(input("Enter the ID of the pilot that you would like to update: "))
            __first_name = input("Enter a new first name (or leave blank to skip): ")
            __family_name = input("Enter a new family name (or leave blank to skip): ")
            __pilot_service.update_pilot(__id, __first_name, __family_name)

        elif __choose_menu == "5":

            print("\n-- REMOVE A PILOT --\n")
            __id = int(input("Enter the ID of the pilot that you would like to delete: "))
            __pilot_service.delete_pilot(__id)

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def airports_menu():
    while True:
        menu_title = "Airports menu"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Show all airports")
        print(" 2. Search airports")
        print(" 3. Add an airport")
        print(" 4. Update an airport")
        print(" 5. Remove an airport")
        print(" 6. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            print("\n-- SHOW ALL AIRPORTS --\n")
            print(__airport_service.get_airport_list())

        elif __choose_menu == "2":

            print("\n-- SEARCH AIRPORTS --\n")
            __code = input("Enter an airport code: ")
            result = __airport_service.search_airports("code", __code)
            print(result)

        elif __choose_menu == "3":

            print("\n-- ADD AN AIRPORT --\n")
            __code = input("Enter the airport code: ")
            __name = input("Enter the airport name: ")
            __city = input("Enter the city: ")
            __country = input("Enter the country: ")
            __region = input("Enter the region: ")
            __airport_service.add_airport(__code, __name, __city, __country, __region)

        elif __choose_menu == "4":

            print("\n-- UPDATE AN AIRPORT --\n")
            __id = int(input("Enter the ID of the airport that you would like to update: "))
            __code = input("Enter a new code (or leave blank to skip): ")
            __name = input("Enter a new name (or leave blank to skip): ")
            __city = input("Enter a new city (or leave blank to skip): ")
            __country = input("Enter a new country (or leave blank to skip): ")
            __region = input("Enter a new region (or leave blank to skip): ")
            __airport_service.update_airport(__id, __code, __name, __city, __country, __region)

        elif __choose_menu == "5":

            print("\n-- REMOVE AN AIRPORT --\n")
            __id = int(input("Enter the ID of the airport that you would like to delete: "))
            __airport_service.delete_airport(__id)

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def aircraft_menu():
    while True:
        menu_title = "Aircraft menu"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Show all aircraft")
        print(" 2. Search aircraft")
        print(" 3. Add an aircraft")
        print(" 4. Update an aircraft")
        print(" 5. Remove an aircraft")
        print(" 6. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            print("\n-- SHOW ALL AIRCRAFT --\n")
            print(__aircraft_service.get_aircraft_list())

        elif __choose_menu == "2":

            print("\n-- SEARCH AIRCRAFT --\n")
            __registration = input("Enter a registration: ")
            result = __aircraft_service.search_aircraft("registration", __registration)
            print(result)

        elif __choose_menu == "3":

            print("\n-- ADD AN AIRCRAFT --\n")
            __registration = input("Enter the aircraft registration: ")
            __manufacturer_serial_no = int(input("Enter the manufacturer serial number: "))
            __icao_hex = input("Enter the ICAO hex code: ")
            __manufacturer = input("Enter the manufacturer: ")
            __model = input("Enter the model: ")
            __icao_type = input("Enter the ICAO type: ")
            __status = input("Enter the aircraft status: ")
            __aircraft_service.add_aircraft(__registration, __manufacturer_serial_no, __icao_hex, __manufacturer, __model, __icao_type, __status)

        elif __choose_menu == "4":

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

        elif __choose_menu == "5":

            print("\n-- REMOVE AN AIRCRAFT --\n")
            __id = int(input("Enter the ID of the aircraft that you would like to delete: "))
            __aircraft_service.delete_aircraft(__id)

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def reports_menu():
    while True:
        menu_title = "Reports menu:"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Pilot statistics")
        print(" 2. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            pass

        elif __choose_menu == "2":
            break
        else:
            print("Invalid Choice")

def admin_menu():
    while True:
        menu_title = "Admin menu"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Initialise database")
        print(" 2. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            __admin_service.initialise_database()
            
        elif __choose_menu == "2":
            break
        else:
            print("Invalid Choice")

print("\nWELCOME TO FLIGHT CLUB!!!!")
main_menu()