from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import prompt_or_cancel
from flightmanagement.services.pilot_service import PilotService


class PilotMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__pilot_service = PilotService()
        self.__session = session
        self.__bindings = bindings

    def load(self):

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
                print(self.__pilot_service.get_pilot_table())

            elif __choose_menu == "search":

                print("\n>> Search for a pilot (or hit CTRL+C to cancel)\n")
                family_name = prompt_or_cancel(self.__session, "Enter a family name: ", "Search cancelled.")
                if family_name is None:                
                    continue
                result = self.__pilot_service.search_pilots("family_name", family_name)
                print(result)

            elif __choose_menu == "add":

                print("\n>> Add a pilot (or hit CTRL+C to cancel)\n")

                first_name = prompt_or_cancel(self.__session, "Enter a first name: ", "Action cancelled.")
                family_name = prompt_or_cancel(self.__session, "Enter a family name: ", "Action cancelled.")

                if first_name is None or family_name is None:
                    continue
                
                print()
                self.__pilot_service.add_pilot(first_name, family_name)

            elif __choose_menu == "update":

                print("\n>> Update a pilot (or hit CTRL+C to cancel)\n")

                id = choice(
                    message="Choose a pilot to update: ",
                    options=self.__pilot_service.get_pilot_choices(),
                    key_bindings=self.__bindings
                )

                # Retrieve the pilot record
                pilot = self.__pilot_service.get_pilot_by_id(id)

                if pilot:

                    print(f"\nEditing information (pilot ID {id})\n")

                    first_name = prompt_or_cancel(self.__session, "First name: ", "Update cancelled", pilot.first_name)
                    family_name = prompt_or_cancel(self.__session, "Family name: ", "Update cancelled", pilot.family_name)

                    if first_name is None or family_name is None:
                        continue

                    print()
                    self.__pilot_service.update_pilot(id, first_name, family_name)

            elif __choose_menu == "delete":

                print("\n>> Delete a pilot (or hit CTRL+C to cancel)\n")

                id = choice(
                    message="Choose a pilot to delete: ",
                    options=self.__pilot_service.get_pilot_choices(),
                    key_bindings=self.__bindings
                )

                print()
                if choice(message="Are you sure you want to delete this record?", options=[(1, "yes"),(0, "no")]) == 1:
                    print()
                    self.__pilot_service.delete_pilot(id)
                else:
                    print("\nDelete cancelled.")

            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice")