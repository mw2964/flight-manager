from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.services.admin_service import AdminService

class AdminMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__admin_service = AdminService()
        self.__session = session
        self.__bindings = bindings

    def load(self):
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

                self.__admin_service.initialise_database()
                
            elif __choose_menu == "back":
                break
            else:
                print("Invalid Choice")