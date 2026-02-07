from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.base_menu import BaseMenu
from flightmanagement.ui.pilot_menu import PilotMenu
from flightmanagement.ui.location_menu import LocationMenu
from flightmanagement.ui.aircraft_menu import AircraftMenu
from flightmanagement.ui.flight_menu import FlightMenu
from flightmanagement.ui.report_menu import ReportMenu
from flightmanagement.ui.admin_menu import AdminMenu

class MainMenu(BaseMenu):
    
    def __init__(self, session, bindings, conn):
        super().__init__(session, bindings, conn)
        
        self._menu_name = "Main Menu"
        self._menu_options = [
            ("flights", "Manage flights"),
            ("pilots", "Manage pilots"),
            ("locations", "Manage destinations"),
            ("aircraft", "Manage aircraft"),
            ("reports", "Reports"),
            ("admin", "Admin"),
            ("exit", "Exit")
        ]

    def load(self):

        while True:

            __choose_menu = choice(
                message = self._format_title(self._menu_name),
                options = self._menu_options
            )

            if __choose_menu == "flights":
                FlightMenu(self._session, self._key_bindings, self._conn).load()
            elif __choose_menu == "pilots":
                PilotMenu(self._session, self._key_bindings, self._conn).load()
            elif __choose_menu == "locations":
                LocationMenu(self._session, self._key_bindings, self._conn).load()
            elif __choose_menu == "aircraft":
                AircraftMenu(self._session, self._key_bindings, self._conn).load()
            elif __choose_menu == "reports":
                ReportMenu(self._session, self._key_bindings, self._conn).load()
            elif __choose_menu == "admin":
                AdminMenu(self._session, self._key_bindings, self._conn).load()
            elif __choose_menu == "exit":
                exit(0)
            else:
                print("Invalid choice")