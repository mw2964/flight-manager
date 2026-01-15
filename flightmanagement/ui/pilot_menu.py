from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel, format_title
from flightmanagement.services.pilot_service import PilotService

class PilotMenu:

    __MENU_NAME = "Pilot menu"
    __MENU_OPTIONS = [
        ("show", "Show all pilots"),
        ("search", "Search pilots"),
        ("add", "Add a pilot"),
        ("update", "Update a pilot"),
        ("delete", "Remove a pilot"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn):
        self.__pilot_service = PilotService(conn)
        self.__session = session
        self.__bindings = bindings

    def __show_option(self) -> None:
        print("\n>> Displaying all pilots\n")
        print(self.__pilot_service.get_pilot_table())

    def __search_option(self) -> bool:
        print("\n>> Search for a pilot (or hit CTRL+C to cancel)\n")

        family_name = prompt_or_cancel(self.__session, "Enter a family name: ", "Search cancelled.")
        if family_name is None:                
            return False
        
        result = self.__pilot_service.search_pilots("family_name", family_name)

        if result is None:
            print("\n     No matching results.")
            return True

        match_count = len(result)
        if match_count == 1:
            print(f"\n     {len(result)} match found:\n")
        else:            
            print(f"\n     {len(result)} matches found:\n")

        print(self.__pilot_service.get_results_view(result))
        return True

    def __add_option(self) -> bool:
        print("\n>> Add a pilot (or hit CTRL+C to cancel)\n")

        first_name = prompt_or_cancel(self.__session, "Enter a first name: ", "Action cancelled.")
        if first_name is None:
            return False

        family_name = prompt_or_cancel(self.__session, "Enter a family name: ", "Action cancelled.")
        if family_name is None:
            return False
        
        print()
        self.__pilot_service.add_pilot(first_name, family_name)
        return True

    def __update_option(self) -> bool:
        print("\n>> Update a pilot (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose a pilot to update: ",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            print("\nUpdate cancelled.")
            return False

        # Retrieve the pilot record
        pilot = self.__pilot_service.get_pilot_by_id(id)

        if pilot:

            print(f"\nEditing information (pilot ID {id})\n")

            first_name = prompt_or_cancel(self.__session, "First name: ", "Update cancelled", pilot.first_name)
            if first_name is None:
                return False

            family_name = prompt_or_cancel(self.__session, "Family name: ", "Update cancelled", pilot.family_name)
            if family_name is None:
                return False

            print()
            self.__pilot_service.update_pilot(id, first_name, family_name)
            
        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete a pilot (or hit CTRL+C to cancel)\n")

        id = choice(
            message="Choose a pilot to delete: ",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if id == "__CANCEL__":
            print("\nDelete cancelled.")
            return False
        
        print()
        if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
            print()
            self.__pilot_service.delete_pilot(id)
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