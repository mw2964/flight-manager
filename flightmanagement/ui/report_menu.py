from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.base_menu import BaseMenu
from flightmanagement.services.report_service import ReportService

class ReportMenu(BaseMenu):

    def __init__(self, session, bindings, conn = None, report_service = None):
        super().__init__(session, bindings, conn)

        self._report_service = report_service or ReportService(conn)
        self._menu_name = "Main -> Reports"
        self._menu_options = [
            ("pilot_stats", "Pilot statistics"),
            ("back", "Back to main menu")
        ]

    def load(self):
        
        while True:

            _selected_option = choice(
                message = self._format_title(self._menu_name),
                options = self._menu_options
            )

            if _selected_option == "pilot_stats":
                print()
                search_text = self._prompt_until_valid(
                    prompt_text = "Enter a search term:",
                    getter = lambda p: p.get_str(),
                    field = "search_text"
                )
                print()
                self._report_service.search_flights(search_text)

            elif _selected_option == "back":
                break
            else:
                print("Invalid Choice")
