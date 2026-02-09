from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.base_menu import BaseMenu
from flightmanagement.services.report_service import ReportService

class ReportMenu(BaseMenu):

    def __init__(self, session, bindings, conn = None, report_service = None):
        super().__init__(session, bindings, conn)

        self._report_service = report_service or ReportService(conn)
        self._menu_name = "Main -> Reports"
        self._menu_options = [
            ("pilot_stats", "Monthly pilot statistics"),
            ("flight_stats", "Monthly flight statistics"),
            ("aircraft_stats", "Monthly aircraft statistics"),
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
                print(self._report_service.pilot_hours_report())

            elif _selected_option == "flight_stats":
                print()
                print(self._report_service.flight_statistics_report())

            elif _selected_option == "aircraft_stats":
                print()
                print(self._report_service.aircraft_statistics_report())

            elif _selected_option == "back":
                break
            else:
                print("Invalid Choice")
