from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel, format_title
from flightmanagement.services.airport_service import AirportService

class AirportMenu:

    __MENU_NAME = "Airports menu"
    __MENU_OPTIONS = [
        ("show", "Show all airports"),
        ("search", "Search airports"),
        ("add", "Add an airport"),
        ("update", "Update an airport"),
        ("delete", "Remove an airport"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn):
        self.__airport_service = AirportService(conn)
        self.__session = session
        self.__bindings = bindings

    def __show_option(self) -> None:
        print("\n>> Displaying all airports\n")
        print(self.__airport_service.get_airport_list())

    def __search_option(self) -> bool:
        print("\n>> Search for an airport (or hit CTRL+C to cancel)\n")

        code = prompt_or_cancel(self.__session, "Enter an airport code: ", "Search cancelled.")
        if code is None:
            return False

        result = self.__airport_service.search_airports("code", code)
        print(result)
        return True

    def __add_option(self) -> bool:
        print("\n>> Add an airport (or hit CTRL+C to cancel)\n")

        code = prompt_or_cancel(self.__session, "Enter the airport code: ", "Action cancelled.")
        if code is None:
            return False
        
        name = prompt_or_cancel(self.__session, "Enter the airport name: ", "Action cancelled.")
        if name is None:
            return False
        
        city = prompt_or_cancel(self.__session, "Enter the city: ", "Action cancelled.")
        if city is None:
            return False
        
        country = prompt_or_cancel(self.__session, "Enter the country: ", "Action cancelled.")
        if country is None:
            return False
        
        region = prompt_or_cancel(self.__session, "Enter the region: ", "Action cancelled.")
        if region is None:
            return False

        print()
        self.__airport_service.add_airport(code, name, city, country, region)
        return True

    def __update_option(self) -> bool:
        print("\n>> Update an airport (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose an airport to update: ",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            print("\nUpdate cancelled.")
            return False

        # Retrieve the airport record
        airport = self.__airport_service.get_airport_by_id(id)

        if airport:

            print(f"\nEditing information (airport ID {id})\n")

            code = prompt_or_cancel(self.__session, "Airport code: ", "Update cancelled", airport.code)
            if code is None:
                return False
            
            name = prompt_or_cancel(self.__session, "Airport name: ", "Update cancelled", airport.name)
            if name is None:
                return False
            
            city = prompt_or_cancel(self.__session, "City: ", "Update cancelled", airport.city)
            if city is None:
                return False
            
            country = prompt_or_cancel(self.__session, "Country): ", "Update cancelled", airport.country)
            if country is None:
                return False
            
            region = prompt_or_cancel(self.__session, "Region: ", "Update cancelled", airport.region)
            if region is None:
                return False

            print()
            self.__airport_service.update_airport(id, code, name, city, country, region)
        
        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete an airport (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose an airport to delete: ",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            return False

        print()
        if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
            print()
            self.__airport_service.delete_airport(id)
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