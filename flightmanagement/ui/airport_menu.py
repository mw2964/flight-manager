from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel
from flightmanagement.services.airport_service import AirportService

class AirportMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__airport_service = AirportService()
        self.__session = session
        self.__bindings = bindings

    def load(self):

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

                print("\n>> Displaying all airports\n")
                print(self.__airport_service.get_airport_list())

            elif __choose_menu == "search":

                print("\n>> Search for an airport (or hit CTRL+C to cancel)\n")
                code = prompt_or_cancel(self.__session, "Enter an airport code: ", "Search cancelled.")
                if code is None:
                    continue
                result = self.__airport_service.search_airports("code", code)
                print(result)

            elif __choose_menu == "add":

                print("\n>> Add an airport (or hit CTRL+C to cancel)\n")

                code = prompt_or_cancel(self.__session, "Enter the airport code: ", "Action cancelled.")
                name = prompt_or_cancel(self.__session, "Enter the airport name: ", "Action cancelled.")
                city = prompt_or_cancel(self.__session, "Enter the city: ", "Action cancelled.")
                country = prompt_or_cancel(self.__session, "Enter the country: ", "Action cancelled.")
                region = prompt_or_cancel(self.__session, "Enter the region: ", "Action cancelled.")
                
                if code is None or name is None or city is None or country is None or region is None:
                    continue

                print()
                self.__airport_service.add_airport(code, name, city, country, region)

            elif __choose_menu == "update":

                print("\n>> Update an airport (or hit CTRL+C to cancel)\n")

                id = choice(
                    message="Choose an airport to update: ",
                    options=self.__airport_service.get_airport_choices(),
                    key_bindings=self.__bindings
                )

                # Retrieve the airport record
                airport = self.__airport_service.get_airport_by_id(id)

                if airport:

                    print(f"\nEditing information (airport ID {id})\n")

                    code = prompt_or_cancel(self.__session, "Airport code: ", "Update cancelled", airport.code)
                    name = prompt_or_cancel(self.__session, "Airport name: ", "Update cancelled", airport.name)
                    city = prompt_or_cancel(self.__session, "City: ", "Update cancelled", airport.city)
                    country = prompt_or_cancel(self.__session, "Country): ", "Update cancelled", airport.country)
                    region = prompt_or_cancel(self.__session, "Region: ", "Update cancelled", airport.region)
                    
                    if code is None or name is None or city is None or country is None or region is None:
                        continue

                    print()
                    self.__airport_service.update_airport(id, code, name, city, country, region)

            elif __choose_menu == "delete":

                print("\n>> Delete an airport (or hit CTRL+C to cancel)\n")

                id = choice(
                    message="Choose an airport to delete: ",
                    options=self.__airport_service.get_airport_choices(),
                    key_bindings=self.__bindings
                )

                print()
                if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
                    print()
                    self.__airport_service.delete_airport(id)
                else:
                    print("\nDelete cancelled.")

            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice")