from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.pilot_menu import PilotMenu
from flightmanagement.ui.airport_menu import AirportMenu
from flightmanagement.ui.aircraft_menu import AircraftMenu
from flightmanagement.ui.flight_menu import FlightMenu
from flightmanagement.ui.report_menu import ReportMenu
from flightmanagement.ui.admin_menu import AdminMenu
from flightmanagement.ui.ui_utils import format_title

class MainMenu:

    __MENU_NAME = "Main menu"
    __MENU_OPTIONS = [
        ("flights", "Flights"),
        ("pilots", "Pilots"),
        ("airports", "Airports"),
        ("aircraft", "Aircraft"),
        ("reports", "Reports"),
        ("admin", "Admin"),
        ("exit", "Exit")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn):
        self.__session = session
        self.__bindings = bindings
        self.conn = conn

    def load(self):

        while True:

            __choose_menu = choice(
                message=format_title(self.__MENU_NAME),
                options=self.__MENU_OPTIONS
            )

            if __choose_menu == "flights":
                FlightMenu(self.__session, self.__bindings, self.conn).load()
            elif __choose_menu == "pilots":
                PilotMenu(self.__session, self.__bindings, self.conn).load()
            elif __choose_menu == "airports":
                AirportMenu(self.__session, self.__bindings, self.conn).load()
            elif __choose_menu == "aircraft":
                AircraftMenu(self.__session, self.__bindings, self.conn).load()
            elif __choose_menu == "reports":
                ReportMenu(self.__session, self.__bindings, self.conn).load()
            elif __choose_menu == "admin":
                AdminMenu(self.__session, self.__bindings, self.conn).load()
            elif __choose_menu == "exit":
                exit(0)
            else:
                print("Invalid choice")