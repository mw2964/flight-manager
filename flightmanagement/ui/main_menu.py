from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.pilot_menu import PilotMenu
from flightmanagement.ui.airport_menu import AirportMenu
from flightmanagement.ui.aircraft_menu import AircraftMenu
from flightmanagement.ui.flight_menu import FlightMenu
from flightmanagement.ui.report_menu import ReportMenu
from flightmanagement.ui.admin_menu import AdminMenu

class MainMenu:

    def __init__(self, session: PromptSession, bindings: KeyBindings):
        self.__session = session
        self.__bindings = bindings

    def load(self):

        while True:
            menu_title = "\nMain menu"
            menu_title = f"{menu_title}\n{"*" * len(menu_title)}"

            __menu_options = [
                ("flights", "Flights"),
                ("pilots", "Pilots"),
                ("airports", "Airports"),
                ("aircraft", "Aircraft"),
                ("reports", "Reports"),
                ("admin", "Admin"),
                ("exit", "Exit")
            ]

            __choose_menu = choice(
                message=menu_title,
                options=__menu_options
            )

            if __choose_menu == "flights":
                FlightMenu(self.__session, self.__bindings).load()
            elif __choose_menu == "pilots":
                PilotMenu(self.__session, self.__bindings).load()
            elif __choose_menu == "airports":
                AirportMenu(self.__session, self.__bindings).load()
            elif __choose_menu == "aircraft":
                AircraftMenu(self.__session, self.__bindings).load()
            elif __choose_menu == "reports":
                ReportMenu(self.__session, self.__bindings).load()
            elif __choose_menu == "admin":
                AdminMenu(self.__session, self.__bindings).load()
            elif __choose_menu == "exit":
                exit(0)
            else:
                print("Invalid choice")