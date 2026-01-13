from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.services.report_service import ReportService

class ReportMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__report_service = ReportService()
        self.__session = session
        self.__bindings = bindings

    def load(self):
        
        while True:

            menu_title = "\nReports menu"
            menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

            __menu_options = [
                ("pilot_stats", "Pilot statistics"),
                ("back", "Back to main menu")
            ]

            __choose_menu = choice(
                message=menu_title,
                options=__menu_options
            )

            if __choose_menu == "pilot_stats":

                pass

            elif __choose_menu == "back":
                break
            else:
                print("Invalid Choice")
