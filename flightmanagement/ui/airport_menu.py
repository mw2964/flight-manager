from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.airport_service import AirportService
from flightmanagement.models.airport import Airport

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

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn=None, airport_service=None):
        self.__airport_service = airport_service or AirportService(conn)
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
        print("\n>> Displaying all airports\n")
        print(self.__airport_service.get_airport_table())

    def __search_option(self) -> bool:
        print("\n>> Search for an airport (or hit CTRL+C to cancel)\n")

        code = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter an airport code: ",
            allow_blank=True
        )        
        if code.is_cancelled:
            return False

        result = self.__airport_service.search_airports("code", code)

        if len(result) == 0:
            print("\n     No matching results.")
        else:
            print(f"\n     {len(result)} match(es) found:\n")
            print(self.__airport_service.get_results_view(result))

        return True

    def __add_option(self) -> bool:
        print("\n>> Add an airport (or hit CTRL+C to cancel)\n")

        # Prompt the user to edit fields
        new = self.__prompt_add_airport()
        if new is None: # Process was cancelled by the user
            return False

        try:
            self.__airport_service.add_airport(new)
            print("\nNew record successfully added.\n")
        except:
            print("\nError adding airport.\n")
       
        return True

    def __update_option(self) -> bool:
        print("\n>> Update an airport (or hit CTRL+C to cancel)\n")

        # Prompt for the airport to edit
        airport = self.__get_airport_from_selection()
        if airport is None or airport.id is None:
            return False
        
        print(f"\nEditing information (airport ID {id})\n")

        # Prompt the user to edit fields
        update = self.__prompt_update_airport(airport)
        if update is None: # Process was cancelled by the user
            return False

        # Update the aircraft record
        try:
            self.__airport_service.update_airport(airport)
            print("\nRecord successfully updated.\n")
        except:
            print("\nError updating pilot.\n")

        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete an airport (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to delete
        airport = self.__prompt_delete_airport()
        if airport is None:
            return False
        
        # Delete the airport
        try:
            self.__airport_service.delete_airport(airport)
            print("\nRecord successfully deleted.\n")
        except:
            print("\nError deleting aircraft.\n")
        
        return True

    def __prompt_add_airport(self) -> Airport | None:

        code = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the airport code: ",
            allow_blank=False
        )        
        if code.is_cancelled:
            return None
        
        name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the airport name: ",
            allow_blank=True
        )        
        if name.is_cancelled:
            return None

        city = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the city: ",            
            allow_blank=True
        )        
        if city.is_cancelled:
            return None
        
        country = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the country: ",
            allow_blank=True
        )        
        if country.is_cancelled:
            return None
        
        region = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the region: ",
            allow_blank=False
        )        
        if region.is_cancelled:
            return None
        print()

        return Airport(
            code=code.value,
            name=name.value,
            city=city.value,
            country=country.value,
            region=region.value
        )

    def __prompt_update_airport(self, airport: Airport) -> Airport | None:
        
        code = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the airport code: ",
            allow_blank=False,
            default_value=airport.code
        )        
        if code.is_cancelled:
            return None
        
        name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the airport name: ",
            allow_blank=True,
            default_value=airport.name
        )        
        if name.is_cancelled:
            return None

        city = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the city: ",
            allow_blank=True,
            default_value=airport.city
        )        
        if city.is_cancelled:
            return None
        
        country = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the country: ",
            allow_blank=True,
            default_value=airport.country
        )        
        if country.is_cancelled:
            return None
        
        region = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the region: ",
            allow_blank=True,
            default_value=airport.region
        )        
        if region.is_cancelled:
            return None
        print()

        return Airport(
            id=airport.id,
            code=code.value,
            name=name.value,
            city=city.value,
            country=country.value,
            region=region.value
        )

    def __prompt_delete_airport(self) -> Airport | None:

        # Prompt for the airport to delete
        airport = self.__get_airport_from_selection()
        if airport is None or airport.id is None:
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
        
        return airport

    def __get_airport_from_selection(self) -> Airport | None:
        airport_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Choose an airport to update:\n",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if airport_id.is_cancelled:
            return None

        return self.__airport_service.get_airport_by_id(int(airport_id.value))