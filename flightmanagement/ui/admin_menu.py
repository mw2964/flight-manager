from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.services.admin_service import AdminService
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt

class AdminMenu:

    __MENU_NAME = "Main -> Admin"
    __MENU_OPTIONS = [
        ("init_db", "Reinitialise database"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn):
        self.__admin_service = AdminService(conn)
        self.__session = session
        self.__bindings = bindings

    def load(self):
        while True:

            __choose_menu = choice(
                message = format_title(self.__MENU_NAME),
                options = self.__MENU_OPTIONS
            )

            if __choose_menu == "init_db":
                confirm = UserPrompt(
                    session = self.__session,
                    prompt_type = "choice",
                    prompt = "\nWARNING - This will reset all data to the example data. Do you wish to continue? \n",
                    options = [
                        ("no", "No"),
                        ("yes", "Yes")
                    ],
                    key_bindings = self.__bindings
                )
                if confirm.is_cancelled:
                    continue
                if confirm.value == "yes":
                    self.__admin_service.initialise_database()
                    print("\nDatabase reinitialised successfully.")
                else:
                    print("\nAction cancelled.")
                
            elif __choose_menu == "back":
                break
            else:
                print("Invalid Choice")