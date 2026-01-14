from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.services.admin_service import AdminService
from flightmanagement.ui.ui_utils import format_title

class AdminMenu:

    __MENU_NAME = "Admin menu"
    __MENU_OPTIONS = [
        ("init_db", "Initialise database"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__admin_service = AdminService()
        self.__session = session
        self.__bindings = bindings

    def load(self):
        while True:

            __choose_menu = choice(
                message=format_title(self.__MENU_NAME),
                options=self.__MENU_OPTIONS
            )

            if __choose_menu == "init_db":

                self.__admin_service.initialise_database()
                
            elif __choose_menu == "back":
                break
            else:
                print("Invalid Choice")