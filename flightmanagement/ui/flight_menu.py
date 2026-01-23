from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.airport_service import AirportService
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.models.flight import Flight

class FlightMenu:

    __MENU_NAME = "Flights menu"
    __MENU_OPTIONS = [
        ("show", "Show all flights"),
        ("search", "Search flights"),
        ("add", "Add a flight"),
        ("update", "Update a flight"),
        ("delete", "Remove a flight"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn=None, flight_service=None, aircraft_service=None, airport_service=None, pilot_service=None):
        self.__flight_service = flight_service or FlightService(conn)
        self.__aircraft_service = aircraft_service or AircraftService(conn)
        self.__airport_service = airport_service or AirportService(conn)
        self.__pilot_service = pilot_service or PilotService(conn)
        self.__session = session
        self.__bindings = bindings

    def load(self):
        while True:
            __choose_menu = choice(message=format_title(self.__MENU_NAME), options=self.__MENU_OPTIONS)

            if __choose_menu == "show":
                self.__show_option()
            elif __choose_menu == "search":                
                if not self.__search_option():
                    print("\nSearch cancelled.\n")
                    continue
            elif __choose_menu == "add":
                if not self.__add_option():
                    print("\nAction cancelled.\n")
                    continue
            elif __choose_menu == "update":
                if not self.__update_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "delete":
                if not self.__delete_option():
                    print("\nDelete cancelled.\n")
                    continue
            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice.")

    def __show_option(self) -> None:
        print("\n>> Displaying all flights\n")
        print(self.__flight_service.get_flight_table())

    def __search_option(self) -> bool:
        print("\n>> Search for a flight (or hit CTRL+C to cancel)\n")

        flight_number = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a flight number: ",
            allow_blank=True
        )        
        if flight_number.is_cancelled:
            return False

        result = self.__flight_service.search_flights("flight_number", flight_number.value)

        if len(result) == 0:
            print("\n     No matching results.")
        else:
            print(f"\n     {len(result)} match(es) found:\n")
            print(self.__flight_service.get_results_view(result))

        return True

    def __add_option(self) -> bool:
        print("\n>> Add a flight (or hit CTRL+C to cancel)\n")

        # Prompt the user to complete fields
        new = self.__prompt_add_flight()
        if new is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.add_flight(new)
            print("\nRecord successfully added.\n")
        except:
            print("\nError adding flight.\n")

        return True

    def __update_option(self) -> bool:
        print("\n>> Update a flight (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to edit
        flight = self.__get_flight_from_selection()
        if flight is None or flight.id is None:
            return False

        print(f"\nEditing information (flight ID {flight.id})\n")

        # Prompt the user to edit fields
        update = self.__prompt_update_flight(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nFlight details successfully updated.\n")
        except:
            print("\nError updating flight.\n")
        
        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete a flight (or hit CTRL+C to cancel)\n")

        # Prompt for the flight to delete
        flight = self.__prompt_delete_flight()
        if flight is None:
            return False
        
        # Delete the flight
        try:
            self.__flight_service.delete_flight(flight)
            print("\nRecord successfully deleted.\n")
        except:
            print("\nError deleting aircraft.\n")
        
        return True
    
    def __prompt_add_flight(self) -> Flight | None:

        flight_number = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a flight number: ",
            allow_blank=False
        )        
        if flight_number.is_cancelled:
            return None
        print()

        aircraft_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the aircraft:\n",
            options=self.__aircraft_service.get_aircraft_choices(),
            key_bindings=self.__bindings
        )
        if aircraft_id.is_cancelled:
            return None
        print()

        origin_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the origin airport:\n",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if origin_id.is_cancelled:
            return None
        print()

        destination_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the destination airport:\n",
            options=self.__airport_service.get_airport_choices(),
            key_bindings=self.__bindings
        )
        if destination_id.is_cancelled:
            return None
        print()

        pilot_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the pilot:\n",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if pilot_id.is_cancelled:
            return None
        print()

        copilot_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the copilot:\n",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if copilot_id.is_cancelled:
            return None
        print()

        departure_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled departure date (DD/MM/YYYY): ",
            allow_blank=False
        )        
        if departure_date.is_cancelled:
            return None

        departure_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled departure time (HH:MM): ",
            allow_blank=False
        )        
        if departure_time.is_cancelled:
            return None

        if departure_date.value == "" or departure_date.value is None:
            arrival_date_default = ""
        else:
            arrival_date_default = datetime.strftime(datetime.strptime(departure_date.value, "%Y-%m-%d"), "%d/%m/%Y")

        arrival_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled arrival date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=arrival_date_default
        )        
        if arrival_date.is_cancelled:
            return None

        arrival_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled arrival time (HH:MM): ",
            allow_blank=False
        )        
        if arrival_time.is_cancelled:
            return None
        
        return Flight(
            flight_number=flight_number.value,
            aircraft_id=int(aircraft_id.value),
            origin_id=int(origin_id.value),
            destination_id=int(destination_id.value),
            pilot_id=int(pilot_id.value),
            copilot_id=int(copilot_id.value),
            departure_time_scheduled=self.combine_date(departure_date.value, departure_time.value),
            arrival_time_scheduled=self.combine_date(arrival_date.value, arrival_time.value)
        )

    def __prompt_update_flight(self, flight: Flight) -> Flight | None:

        flight_number = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a flight number: ",
            allow_blank=False,
            default_value=flight.flight_number
        )        
        if flight_number.is_cancelled:
            return None
        print()
        
        aircraft_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the aircraft:\n",
            options=self.__aircraft_service.get_aircraft_choices(),
            default_value=flight.aircraft_id,
            key_bindings=self.__bindings
        )
        if aircraft_id.is_cancelled:
            return None
        print()

        origin_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the origin airport:\n",
            options=self.__airport_service.get_airport_choices(),
            default_value=flight.origin_id,
            key_bindings=self.__bindings
        )
        if origin_id.is_cancelled:
            return None
        print()

        destination_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the destination airport:\n",
            options=self.__airport_service.get_airport_choices(),
            default_value=flight.destination_id,
            key_bindings=self.__bindings
        )
        if destination_id.is_cancelled:
            return None
        print()

        pilot_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the pilot:\n",
            options=self.__pilot_service.get_pilot_choices(),
            default_value=flight.pilot_id,
            key_bindings=self.__bindings
        )
        if pilot_id.is_cancelled:
            return None
        print()

        copilot_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the copilot:\n",
            options=self.__pilot_service.get_pilot_choices(),
            default_value=flight.copilot_id,
            key_bindings=self.__bindings
        )
        if copilot_id.is_cancelled:
            return None
        print()

        departure_date_scheduled = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled departure date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=self.date_string_from_datetime(flight.departure_time_scheduled)
        )        
        if departure_date_scheduled.is_cancelled:
            return None

        departure_time_scheduled = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled departure time (HH:MM): ",
            allow_blank=False,
            default_value=self.time_string_from_datetime(flight.departure_time_scheduled)
        )        
        if departure_time_scheduled.is_cancelled:
            return None

        arrival_date_scheduled = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled departure date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=self.date_string_from_datetime(flight.arrival_time_scheduled)
        )      
        if arrival_date_scheduled.is_cancelled:
            return None

        arrival_time_scheduled = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled departure time (HH:MM): ",
            allow_blank=True,
            default_value=self.time_string_from_datetime(flight.arrival_time_scheduled)
        )        
        if arrival_time_scheduled.is_cancelled:
            return None

        departure_date_actual = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Actual departure date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=self.date_string_from_datetime(flight.departure_time_actual)
        )     
        if departure_date_actual.is_cancelled:
            return None

        departure_time_actual = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Actual departure time (HH:MM): ",
            allow_blank=True,
            default_value=self.time_string_from_datetime(flight.departure_time_actual)
        )        
        if departure_time_actual.is_cancelled:
            return None

        arrival_date_actual = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Actual arrival date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=self.date_string_from_datetime(flight.arrival_time_actual)
        )   
        if arrival_date_actual.is_cancelled:
            return None

        arrival_time_actual = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Actual arrival time (HH:MM): ",
            allow_blank=True,
            default_value=self.time_string_from_datetime(flight.arrival_time_actual)
        )        
        if arrival_time_actual.is_cancelled:
            return None
        print()

        status = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select a flight status:\n",
            options=[
                ("Scheduled", ("Scheduled")),
                ("Delayed", ("Delayed")),
                ("On time", ("On time")),
                ("Boarding", ("Boarding")),
                ("Closed", ("Closed")),
                ("Departed", ("Departed")),
                ("Arrived", ("Arrived"))
            ],
            default_value=flight.status,
            key_bindings=self.__bindings
        )
        if status.is_cancelled:
            return None
        print()

        # Format datetimes, checking against partial values
        departure_datetime_scheduled_formatted = self.combine_date(departure_date_scheduled.value, departure_time_scheduled.value)
        arrival_datetime_scheduled_formatted = self.combine_date(arrival_date_scheduled.value, arrival_time_scheduled.value) if arrival_date_scheduled and arrival_time_scheduled else None
        departure_datetime_actual_formatted = self.combine_date(departure_date_actual.value, departure_time_actual.value) if departure_date_actual and departure_time_actual else None
        arrival_datetime_actual_formatted = self.combine_date(arrival_date_actual.value, arrival_time_actual.value) if arrival_date_actual and arrival_time_actual else None

        return Flight(
            id=flight.id,
            flight_number=flight_number.value,
            aircraft_id=int(aircraft_id.value),
            origin_id=int(origin_id.value),
            destination_id=int(destination_id.value),
            pilot_id=int(pilot_id.value),
            copilot_id=int(copilot_id.value),
            departure_time_scheduled=departure_datetime_scheduled_formatted,
            arrival_time_scheduled=arrival_datetime_scheduled_formatted,
            departure_time_actual=departure_datetime_actual_formatted,
            arrival_time_actual=arrival_datetime_actual_formatted,
            status=status.value
        )

    def __prompt_delete_flight(self) -> Flight | None:

        # Prompt for the flight to delete
        flight = self.__get_flight_from_selection()
        if flight is None or flight.id is None:
            return None
        
        # Prompt for confirmation and delete if confirmed
        confirm = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Are you sure you want to delete this record?\n",
            options=[(1, "yes"),(0, "no")],
            key_bindings=self.__bindings
        )

        if confirm.is_cancelled or confirm.value == False:
            return None
        
        return flight

    def __get_flight_from_selection(self) -> Flight | None:
        flight_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Choose a flight to update:\n",
            options=self.__flight_service.get_flight_choices(),
            key_bindings=self.__bindings
        )
        if flight_id.is_cancelled:
            return None

        return self.__flight_service.get_flight_by_id(int(flight_id.value))

    def combine_date(self, date: str, time: str) -> datetime:
        
        # If either date or time are empty, return None
        if date is None or time is None:
            return None
        
        return datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    
    def date_string_from_datetime(self, input: datetime | None) -> str | None:
        if input is None:
            return None
        
        return datetime.strftime(input, "%d/%m/%Y")
    
    def time_string_from_datetime(self, input: datetime | None) -> str | None:
        if input is None:
            return None
        
        return datetime.strftime(input, "%H:%M")