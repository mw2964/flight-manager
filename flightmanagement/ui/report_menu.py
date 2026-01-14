from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.services.report_service import ReportService
from flightmanagement.ui.ui_utils import format_title

class ReportMenu:

    __MENU_NAME = "Reports menu"
    __MENU_OPTIONS = [
        ("pilot_stats", "Pilot statistics"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__report_service = ReportService()
        self.__session = session
        self.__bindings = bindings

    def load(self):
        
        while True:

            __choose_menu = choice(
                message=format_title(self.__MENU_NAME),
                options=self.__MENU_OPTIONS
            )

            if __choose_menu == "pilot_stats":

                pass

            elif __choose_menu == "back":
                break
            else:
                print("Invalid Choice")
