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

class FlightUpdateMenu:

    __MENU_NAME = "What would you like to do?"
    __MENU_OPTIONS = [
        ("assign_pilot", "Assign pilot and/or copilot"),
        ("update_aircraft", "Change aircraft"),
        ("update_status", "Update flight status"),
        ("update_scheduled_times", "Update scheduled times"),
        ("log_departure", "Log departure"),
        ("log_arrival", "Log arrival"),
        ("back", "Back to flights menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, flight_id: int, conn=None, flight_service=None, aircraft_service=None, airport_service=None, pilot_service=None):
        self.__flight_service = flight_service or FlightService(conn)
        self.__aircraft_service = aircraft_service or AircraftService(conn)
        self.__airport_service = airport_service or AirportService(conn)
        self.__pilot_service = pilot_service or PilotService(conn)
        self.__session = session
        self.__bindings = bindings
        self.__flight_id = flight_id

    def load(self):
        
        print(f"\nUpdating flight ID {self.__flight_id}:\n")
        self.__show_flight_summary()
        
        while True:            

            __choose_menu = choice(message=format_title(self.__MENU_NAME, False), options=self.__MENU_OPTIONS)

            if __choose_menu == "assign_pilot":
                if not self.__assign_pilot_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "update_aircraft":                
                if not self.__update_aircraft_option():
                    print("\nUpdate cancelled.\n")
                    continue            
            elif __choose_menu == "update_status":                
                if not self.__update_status_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "update_scheduled_times":
                if not self.__update_scheduled_times_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "log_departure":
                if not self.__log_departure_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "log_arrival":
                if not self.__log_arrival_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "update_all":
                if not self.__update_all_option():
                    print("\nUpdate cancelled.\n")
                    continue
            elif __choose_menu == "back":
                return
            else:
                print("Invalid choice.")
    
    def __show_flight_summary(self):        
        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return 
        print(self.__flight_service.get_results_view([flight]))

    def __assign_pilot_option(self) -> bool:
        print("\n>> Assign a pilot (or hit CTRL+C to cancel)\n")

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_assign_pilot(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True

    def __update_aircraft_option(self) -> bool:
        print("\n>> Update the aircraft (or hit CTRL+C to cancel)\n")

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_update_aircraft(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nAircraft successfully updated:\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True
    
    def __update_status_option(self) -> bool:
        print("\n>> Update the flight status (or hit CTRL+C to cancel)\n")

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_update_status(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nStatus successfully updated:\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True

    def __update_scheduled_times_option(self) -> bool:
        print("\n>> Update the scheduled departure and arrival times (or hit CTRL+C to cancel)\n")

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_update_scheduled_times(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True

    def __log_departure_option(self) -> bool:
        print("\n>> Log the actual departure time and set status to 'departed' (or hit CTRL+C to cancel)\n")

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_log_departure(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True
    
    def __log_arrival_option(self) -> bool:
        print("\n>> Log the actual arrival time and set status to 'arrived' (or hit CTRL+C to cancel)\n")

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_log_arrival(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True

    def __update_all_option(self) -> bool:
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

    def __prompt_log_departure(self, flight: Flight) -> Flight | None:

        date_default = self.date_string_from_datetime(flight.departure_time_actual) if flight.departure_time_actual else self.date_string_from_datetime(flight.departure_time_scheduled)
        time_default = self.time_string_from_datetime(flight.departure_time_actual) if flight.departure_time_actual else self.time_string_from_datetime(flight.departure_time_scheduled)

        departure_date_actual = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Actual departure date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=date_default
        )     
        if departure_date_actual.is_cancelled:
            return None

        departure_time_actual = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Actual departure time (HH:MM): ",
            allow_blank=True,
            default_value=time_default
        )        
        if departure_time_actual.is_cancelled:
            return None

        departure_datetime_actual_formatted = self.combine_date(departure_date_actual.value, departure_time_actual.value) if departure_date_actual and departure_time_actual else None

        return Flight(
            id=flight.id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_id=flight.origin_id,
            destination_id=flight.destination_id,
            pilot_id=flight.pilot_id,
            copilot_id=flight.copilot_id,
            departure_time_scheduled=flight.departure_time_scheduled,
            arrival_time_scheduled=flight.arrival_time_scheduled,
            departure_time_actual=departure_datetime_actual_formatted,
            arrival_time_actual=flight.arrival_time_actual,
            status="Departed"
        )

    def __prompt_update_scheduled_times(self, flight: Flight) -> Flight | None:

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

        # Format datetimes, checking against partial values
        departure_datetime_scheduled_formatted = self.combine_date(departure_date_scheduled.value, departure_time_scheduled.value)
        arrival_datetime_scheduled_formatted = self.combine_date(arrival_date_scheduled.value, arrival_time_scheduled.value) if arrival_date_scheduled and arrival_time_scheduled else None
 
        return Flight(
            id=flight.id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_id=flight.origin_id,
            destination_id=flight.destination_id,
            pilot_id=flight.pilot_id,
            copilot_id=flight.copilot_id,
            departure_time_scheduled=departure_datetime_scheduled_formatted,
            arrival_time_scheduled=arrival_datetime_scheduled_formatted,
            departure_time_actual=flight.departure_time_actual,
            arrival_time_actual=flight.arrival_time_actual,
            status=flight.status
        )

    def __prompt_log_arrival(self, flight: Flight) -> Flight | None:

        date_default = self.date_string_from_datetime(flight.arrival_time_actual) if flight.arrival_time_actual else self.date_string_from_datetime(flight.arrival_time_scheduled)
        time_default = self.time_string_from_datetime(flight.arrival_time_actual) if flight.arrival_time_actual else self.time_string_from_datetime(flight.arrival_time_scheduled)

        arrival_date_actual = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Actual arrival date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=date_default
        )     
        if arrival_date_actual.is_cancelled:
            return None

        arrival_time_actual = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Actual arrival time (HH:MM): ",
            allow_blank=True,
            default_value=time_default
        )        
        if arrival_time_actual.is_cancelled:
            return None

        arrival_datetime_actual_formatted = self.combine_date(arrival_date_actual.value, arrival_time_actual.value) if arrival_date_actual and arrival_time_actual else None

        return Flight(
            id=flight.id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_id=flight.origin_id,
            destination_id=flight.destination_id,
            pilot_id=flight.pilot_id,
            copilot_id=flight.copilot_id,
            departure_time_scheduled=flight.departure_time_scheduled,
            arrival_time_scheduled=flight.arrival_time_scheduled,
            departure_time_actual=flight.departure_time_actual,
            arrival_time_actual=arrival_datetime_actual_formatted,
            status="Arrived"
        )

    def __prompt_update_status(self, flight: Flight) -> Flight | None:

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

        return Flight(
            id=flight.id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_id=flight.origin_id,
            destination_id=flight.destination_id,
            pilot_id=flight.pilot_id,
            copilot_id=flight.copilot_id,
            departure_time_scheduled=flight.departure_time_scheduled,
            arrival_time_scheduled=flight.arrival_time_scheduled,
            departure_time_actual=flight.departure_time_actual,
            arrival_time_actual=flight.arrival_time_actual,
            status=status.value
        )

    def __prompt_update_aircraft(self, flight: Flight) -> Flight | None:

        aircraft_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select an aircraft:\n",
            options=self.__aircraft_service.get_aircraft_choices(),
            default_value=flight.aircraft_id,
            key_bindings=self.__bindings
        )
        if aircraft_id.is_cancelled:
            return None
        print()

        return Flight(
            id=flight.id,
            flight_number=flight.flight_number,
            aircraft_id=int(aircraft_id.value),
            origin_id=flight.origin_id,
            destination_id=flight.destination_id,
            pilot_id=flight.pilot_id,
            copilot_id=flight.copilot_id,
            departure_time_scheduled=flight.departure_time_scheduled,
            arrival_time_scheduled=flight.arrival_time_scheduled,
            departure_time_actual=flight.departure_time_actual,
            arrival_time_actual=flight.arrival_time_actual,
            status=flight.status
        )

    def __prompt_assign_pilot(self, flight: Flight) -> Flight | None:

        assign_choice = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Would you like to assign a pilot, a copilot, or both?\n",
            options=[
                ("pilot", ("Pilot")),
                ("copilot", ("Copilot")),
                ("both", ("Both"))
            ],
            key_bindings=self.__bindings
        )
        if assign_choice.is_cancelled:
            return None
        print()

        pilot_id = None
        copilot_id = None

        if assign_choice.value in ["pilot", "both"]:
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

        if assign_choice.value in ["copilot", "both"]:
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

        return Flight(
            id=flight.id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_id=flight.origin_id,
            destination_id=flight.destination_id,
            pilot_id=int(pilot_id.value) if pilot_id else flight.pilot_id,
            copilot_id=int(copilot_id.value) if copilot_id else flight.copilot_id,
            departure_time_scheduled=flight.departure_time_scheduled,
            arrival_time_scheduled=flight.arrival_time_scheduled,
            departure_time_actual=flight.departure_time_actual,
            arrival_time_actual=flight.arrival_time_actual,
            status=flight.status
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