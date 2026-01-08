from flightmanagement.services.userservice import UserService

user_service = UserService()

def main_menu():
    while True:
        menu_title = "Main menu:"
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
        menu_title = "Flights menu:"
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
            print(user_service.get_all_flight_details())

        elif __choose_menu == "2":

            print("\n-- SEARCH FLIGHTS --\n")
            
        elif __choose_menu == "3":

            print("\n-- ADD A FLIGHT --\n")
            
        elif __choose_menu == "4":

            print("\n-- UPDATE A FLIGHT --\n")

        elif __choose_menu == "5":

            print("\n-- REMOVE A FLIGHT --\n")

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def pilots_menu():
    while True:
        menu_title = "Pilots menu:"
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
            print(user_service.get_pilot_list())

        elif __choose_menu == "2":

            print("\n-- SEARCH PILOTS --\n")
            __family_name = input("Enter a family name: ")
            result = user_service.search_pilots("family_name", __family_name)
            print(result)

        elif __choose_menu == "3":

            print("\n-- ADD A PILOT --\n")
            __first_name = input("Enter a first name: ")
            __family_name = input("Enter a family name: ")
            user_service.add_pilot(__first_name, __family_name)

        elif __choose_menu == "4":

            print("\n-- UPDATE A PILOT --\n")
            __id = int(input("Enter the ID of the pilot that you would like to update: "))
            __first_name = input("Enter a new first name (or leave blank to skip): ")
            __family_name = input("Enter a new family name (or leave blank to skip): ")
            user_service.update_pilot(__id, __first_name, __family_name)

        elif __choose_menu == "5":

            print("\n-- REMOVE A PILOT --\n")
            __id = int(input("Enter the ID of the pilot that you would like to delete: "))
            user_service.delete_pilot(__id)

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def airports_menu():
    while True:
        menu_title = "Airports menu:"
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
            print(user_service.get_airport_list())

        elif __choose_menu == "2":

            print("\n-- SEARCH AIRPORTS --\n")
            __code = input("Enter an airport code: ")
            result = user_service.search_airports("code", __code)
            print(result)

        elif __choose_menu == "3":

            print("\n-- ADD AN AIRPORT --\n")
            __code = input("Enter the airport code: ")
            __name = input("Enter the airport name: ")
            __city = input("Enter the city: ")
            __country = input("Enter the country: ")
            __region = input("Enter the region: ")
            user_service.add_airport(__code, __name, __city, __country, __region)

        elif __choose_menu == "4":

            print("\n-- UPDATE AN AIRPORT --\n")
            __id = int(input("Enter the ID of the airport that you would like to update: "))
            __code = input("Enter a new code (or leave blank to skip): ")
            __name = input("Enter a new name (or leave blank to skip): ")
            __city = input("Enter a new city (or leave blank to skip): ")
            __country = input("Enter a new country (or leave blank to skip): ")
            __region = input("Enter a new region (or leave blank to skip): ")
            user_service.update_airport(__id, __code, __name, __city, __country, __region)

        elif __choose_menu == "5":

            print("\n-- REMOVE AN AIRPORT --\n")
            __id = int(input("Enter the ID of the aiport that you would like to delete: "))
            user_service.delete_airport(__id)

        elif __choose_menu == "6":
            break
        else:
            print("Invalid Choice")

def aircraft_menu():
    while True:
        menu_title = "Aircraft menu:"
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

            pass

        elif __choose_menu == "2":

            pass

        elif __choose_menu == "3":

            pass

        elif __choose_menu == "4":

            pass

        elif __choose_menu == "5":

            pass

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
        menu_title = "Admin menu:"
        print(f"\n{menu_title}")
        print("*" * len(menu_title))
        print(" 1. Initialise database")
        print(" 2. Back to main menu")
        print("")

        __choose_menu = input("Enter your choice: ")

        if __choose_menu == "1":

            user_service.initialise_database()
            
        elif __choose_menu == "2":
            break
        else:
            print("Invalid Choice")

main_menu()

