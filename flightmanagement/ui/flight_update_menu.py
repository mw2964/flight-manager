from datetime import datetime, date, time
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.location_service import LocationService
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
        ("update_all", "Update all flight details"),
        ("back", "Back to flights menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, flight_id: int, conn=None, flight_service=None, aircraft_service=None, location_service=None, pilot_service=None):
        self.__flight_service = flight_service or FlightService(conn)
        self.__aircraft_service = aircraft_service or AircraftService(conn)
        self.__location_service = location_service or LocationService(conn)
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

        flight = self.__flight_service.get_flight_by_id(self.__flight_id)
        if flight is None:
            return False

        # Prompt the user to edit fields
        update = self.__prompt_update_flight(flight)
        if update is None: # Process was cancelled by the user
            return False

        try:
            self.__flight_service.update_flight(update)
            print("\nFlight details successfully updated.\n")
            self.__show_flight_summary()
        except:
            print("\nError updating flight.\n")
        
        return True

    def __prompt_log_departure(self, flight: Flight) -> Flight | None:

        confirmed_departure_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Confirmed departure date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=flight.scheduled_departure_date.strftime("%d/%m/%Y")
        )     
        if confirmed_departure_date.is_cancelled:
            return None

        confirmed_departure_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Confirmed departure time (HH:MM): ",
            allow_blank=True,
            default_value=flight.scheduled_departure_time.strftime("%H:%M")
        )        
        if confirmed_departure_time.is_cancelled:
            return None

        return Flight(
            flight_id=flight.flight_id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_location_id=flight.origin_location_id,
            destination_location_id=flight.destination_location_id,
            departure_gate_id=flight.departure_gate_id,
            arrival_gate_id=flight.arrival_gate_id,
            captain_id=flight.captain_id,
            first_officer_id=flight.first_officer_id,
            scheduled_departure_date=flight.scheduled_departure_date,
            scheduled_departure_time=flight.scheduled_departure_time,
            scheduled_arrival_date=flight.scheduled_arrival_date,
            scheduled_arrival_time=flight.scheduled_arrival_time,
            confirmed_departure_date=date.fromisoformat(confirmed_departure_date.value) if confirmed_departure_date.value else None,
            confirmed_departure_time=time.fromisoformat(confirmed_departure_time.value) if confirmed_departure_time.value else None,
            confirmed_arrival_date=flight.confirmed_arrival_date,
            confirmed_arrival_time=flight.confirmed_arrival_time,
            flight_status="Departed"
        )

    def __prompt_update_scheduled_times(self, flight: Flight) -> Flight | None:

        scheduled_departure_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled departure date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=flight.scheduled_departure_date.strftime("%d/%m/%Y")
        )        
        if scheduled_departure_date.is_cancelled:
            return None

        scheduled_departure_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled departure time (HH:MM): ",
            allow_blank=False,
            default_value=flight.scheduled_departure_time.strftime("%H:%M")
        )        
        if scheduled_departure_time.is_cancelled:
            return None

        scheduled_arrival_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled departure date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=flight.scheduled_arrival_date.strftime("%d/%m/%Y")
        )      
        if scheduled_arrival_date.is_cancelled:
            return None

        scheduled_arrival_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled departure time (HH:MM): ",
            allow_blank=False,
            default_value=flight.scheduled_arrival_time.strftime("%H:%M")
        )        
        if scheduled_arrival_time.is_cancelled:
            return None

        return Flight(
            flight_id=flight.flight_id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_location_id=flight.origin_location_id,
            destination_location_id=flight.destination_location_id,
            departure_gate_id=flight.departure_gate_id,
            arrival_gate_id=flight.arrival_gate_id,
            captain_id=flight.captain_id,
            first_officer_id=flight.first_officer_id,
            scheduled_departure_date=date.fromisoformat(scheduled_departure_date.value),
            scheduled_departure_time=time.fromisoformat(scheduled_departure_time.value),
            scheduled_arrival_date=date.fromisoformat(scheduled_arrival_date.value),
            scheduled_arrival_time=time.fromisoformat(scheduled_arrival_time.value),
            confirmed_departure_date=flight.confirmed_departure_date,
            confirmed_departure_time=flight.confirmed_departure_time,
            confirmed_arrival_date=flight.confirmed_arrival_date,
            confirmed_arrival_time=flight.confirmed_arrival_time,
            flight_status="Departed"
        )

    def __prompt_log_arrival(self, flight: Flight) -> Flight | None:

        confirmed_arrival_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Actual arrival date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=flight.scheduled_arrival_date.strftime("%d/%m/%Y")
        )     
        if confirmed_arrival_date.is_cancelled:
            return None

        confirmed_arrival_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Actual arrival time (HH:MM): ",
            allow_blank=False,
            default_value=flight.scheduled_arrival_time.strftime("%H:%M")
        )        
        if confirmed_arrival_time.is_cancelled:
            return None

        return Flight(
            flight_id=flight.flight_id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_location_id=flight.origin_location_id,
            destination_location_id=flight.destination_location_id,
            departure_gate_id=flight.departure_gate_id,
            arrival_gate_id=flight.arrival_gate_id,
            captain_id=flight.captain_id,
            first_officer_id=flight.first_officer_id,
            scheduled_departure_date=flight.scheduled_departure_date,
            scheduled_departure_time=flight.scheduled_departure_time,
            scheduled_arrival_date=flight.scheduled_arrival_date,
            scheduled_arrival_time=flight.scheduled_arrival_time,
            confirmed_departure_date=flight.confirmed_departure_date,
            confirmed_departure_time=flight.confirmed_departure_time,
            confirmed_arrival_date=date.fromisoformat(confirmed_arrival_date.value),
            confirmed_arrival_time=time.fromisoformat(confirmed_arrival_time.value),
            flight_status="Arrived"
        )

    def __prompt_update_status(self, flight: Flight) -> Flight | None:

        flight_status = UserPrompt(
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
            default_value=flight.flight_status,
            key_bindings=self.__bindings
        )
        if flight_status.is_cancelled:
            return None
        print()

        return Flight(
            flight_id=flight.flight_id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_location_id=flight.origin_location_id,
            destination_location_id=flight.destination_location_id,
            departure_gate_id=flight.departure_gate_id,
            arrival_gate_id=flight.arrival_gate_id,
            captain_id=flight.captain_id,
            first_officer_id=flight.first_officer_id,
            scheduled_departure_date=flight.scheduled_departure_date,
            scheduled_departure_time=flight.scheduled_departure_time,
            scheduled_arrival_date=flight.scheduled_arrival_date,
            scheduled_arrival_time=flight.scheduled_arrival_time,
            confirmed_departure_date=flight.confirmed_departure_date,
            confirmed_departure_time=flight.confirmed_departure_time,
            confirmed_arrival_date=flight.confirmed_arrival_date,
            confirmed_arrival_time=flight.confirmed_arrival_time,
            flight_status=flight_status.value
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
            flight_id=flight.flight_id,
            flight_number=flight.flight_number,
            aircraft_id=int(aircraft_id.value),
            origin_location_id=flight.origin_location_id,
            destination_location_id=flight.destination_location_id,
            departure_gate_id=flight.departure_gate_id,
            arrival_gate_id=flight.arrival_gate_id,
            captain_id=flight.captain_id,
            first_officer_id=flight.first_officer_id,
            scheduled_departure_date=flight.scheduled_departure_date,
            scheduled_departure_time=flight.scheduled_departure_time,
            scheduled_arrival_date=flight.scheduled_arrival_date,
            scheduled_arrival_time=flight.scheduled_arrival_time,
            confirmed_departure_date=flight.confirmed_departure_date,
            confirmed_departure_time=flight.confirmed_departure_time,
            confirmed_arrival_date=flight.confirmed_arrival_date,
            confirmed_arrival_time=flight.confirmed_arrival_time,
            flight_status=flight.flight_status
        )

    def __prompt_assign_pilot(self, flight: Flight) -> Flight | None:

        assign_choice = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Would you like to assign the captain, the first officer, or both?\n",
            options=[
                ("captain", ("Captain")),
                ("first_officer", ("First officer")),
                ("both", ("Both"))
            ],
            key_bindings=self.__bindings
        )
        if assign_choice.is_cancelled:
            return None
        print()

        captain_id = None
        first_officer_id = None

        if assign_choice.value in ["captain", "both"]:
            captain_id = UserPrompt(
                session=self.__session,
                prompt_type="choice",
                prompt="Select the pilot:\n",
                options=self.__flight_service.get_available_pilot_choices(
                    datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                    datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                    flight.flight_id
                ),
                default_value=flight.captain_id,
                key_bindings=self.__bindings
            )
            if captain_id.is_cancelled:
                return None
            print()

        if assign_choice.value in ["first_officer", "both"]:
            first_officer_id = UserPrompt(
                session=self.__session,
                prompt_type="choice",
                prompt="Select the copilot:\n",
                options=self.__flight_service.get_available_pilot_choices(
                    datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                    datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                    flight.flight_id,
                    int(captain_id.value) if captain_id else flight.captain_id
                ),
                default_value=flight.first_officer_id,
                key_bindings=self.__bindings
            )
            if first_officer_id.is_cancelled:
                return None
            print()

        return Flight(
            flight_id=flight.flight_id,
            flight_number=flight.flight_number,
            aircraft_id=flight.aircraft_id,
            origin_location_id=flight.origin_location_id,
            destination_location_id=flight.destination_location_id,
            departure_gate_id=flight.departure_gate_id,
            arrival_gate_id=flight.arrival_gate_id,
            captain_id=int(captain_id.value) if captain_id else flight.captain_id,
            first_officer_id=int(first_officer_id.value) if first_officer_id else flight.first_officer_id,
            scheduled_departure_date=flight.scheduled_departure_date,
            scheduled_departure_time=flight.scheduled_departure_time,
            scheduled_arrival_date=flight.scheduled_arrival_date,
            scheduled_arrival_time=flight.scheduled_arrival_time,
            confirmed_departure_date=flight.confirmed_departure_date,
            confirmed_departure_time=flight.confirmed_departure_time,
            confirmed_arrival_date=flight.confirmed_arrival_date,
            confirmed_arrival_time=flight.confirmed_arrival_time,
            flight_status=flight.flight_status
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

        origin_location_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the origin location:\n",
            options=self.__location_service.get_location_choices(),
            default_value=flight.origin_location_id,
            key_bindings=self.__bindings
        )
        if origin_location_id.is_cancelled:
            return None
        print()

        destination_location_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the destination location:\n",
            options=self.__location_service.get_location_choices(),
            default_value=flight.destination_location_id,
            key_bindings=self.__bindings
        )
        if destination_location_id.is_cancelled:
            return None
        print()

        scheduled_departure_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled departure date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=flight.scheduled_departure_date.strftime("%d/%m/%Y")
        )        
        if scheduled_departure_date.is_cancelled:
            return None

        scheduled_departure_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled departure time (HH:MM): ",
            allow_blank=False,
            default_value=flight.scheduled_departure_time.strftime("%H:%M")
        )        
        if scheduled_departure_time.is_cancelled:
            return None

        scheduled_arrival_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Scheduled arrival date (DD/MM/YYYY): ",
            allow_blank=False,
            default_value=flight.scheduled_arrival_date.strftime("%d/%m/%Y")
        )      
        if scheduled_arrival_date.is_cancelled:
            return None

        scheduled_arrival_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Scheduled arrival time (HH:MM): ",
            allow_blank=False,
            default_value=flight.scheduled_arrival_time.strftime("%H:%M")
        )        
        if scheduled_arrival_time.is_cancelled:
            return None
        print()

        captain_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the pilot:\n",
            options=self.__flight_service.get_available_pilot_choices(
                datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                flight.flight_id
            ),
            default_value=flight.captain_id,
            key_bindings=self.__bindings
        )
        if captain_id.is_cancelled:
            return None
        print()

        first_officer_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the copilot:\n",
            options=self.__flight_service.get_available_pilot_choices(
                datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                flight.flight_id,
                int(captain_id.value) if captain_id else flight.captain_id
            ),
            default_value=flight.first_officer_id,
            key_bindings=self.__bindings
        )
        if first_officer_id.is_cancelled:
            return None
        print()

        departure_terminal_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the departure terminal:\n",
            options=self.__location_service.get_airport_terminal_choices(int(origin_location_id.value)),
            default_value=flight.first_officer_id,
            key_bindings=self.__bindings,
            allow_skip=True
        )
        if departure_terminal_id.is_cancelled:
            return None
        print()

        departure_gate_id = None
        if departure_terminal_id.value != "":
            departure_gate_id = UserPrompt(
                session=self.__session,
                prompt_type="choice",
                prompt="Select the departure terminal:\n",
                options=self.__location_service.get_terminal_gate_choices(int(departure_terminal_id.value)),
                default_value=flight.first_officer_id,
                key_bindings=self.__bindings,
                allow_skip=True
            )
            if departure_gate_id.is_cancelled:
                return None
            print()

        confirmed_departure_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Confirmed departure date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=flight.confirmed_departure_date.strftime("%d/%m/%Y") if flight.confirmed_departure_date else None
        )     
        if confirmed_departure_date.is_cancelled:
            return None

        confirmed_departure_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Confirmed departure time (HH:MM): ",
            allow_blank=True,
            default_value=flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None
        )        
        if confirmed_departure_time.is_cancelled:
            return None
        print()

        arrival_terminal_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select the arrival terminal:\n",
            options=self.__location_service.get_airport_terminal_choices(int(destination_location_id.value)),
            default_value=flight.first_officer_id,
            key_bindings=self.__bindings,
            allow_skip=True
        )
        if arrival_terminal_id.is_cancelled:
            return None
        print()

        arrival_gate_id = None
        if arrival_terminal_id.value != "":
            arrival_gate_id = UserPrompt(
                session=self.__session,
                prompt_type="choice",
                prompt="Select the arrival terminal:\n",
                options=self.__location_service.get_terminal_gate_choices(int(arrival_terminal_id.value)),
                default_value=flight.first_officer_id,
                key_bindings=self.__bindings,
                allow_skip=True
            )
            if arrival_gate_id.is_cancelled:
                return None
            print()

        confirmed_arrival_date = UserPrompt(
            session=self.__session,
            prompt_type="date",
            prompt="Confirmed arrival date (DD/MM/YYYY): ",
            allow_blank=True,
            default_value=flight.confirmed_arrival_date.strftime("%d/%m/%Y") if flight.confirmed_arrival_date else None
        )   
        if confirmed_arrival_date.is_cancelled:
            return None

        confirmed_arrival_time = UserPrompt(
            session=self.__session,
            prompt_type="time",
            prompt="Confirmed arrival time (HH:MM): ",
            allow_blank=True,
            default_value=flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None
        )        
        if confirmed_arrival_time.is_cancelled:
            return None
        print()

        flight_status = UserPrompt(
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
            default_value=flight.flight_status,
            key_bindings=self.__bindings
        )
        if flight_status.is_cancelled:
            return None
        print()

        return Flight(
            flight_id = flight.flight_id,
            flight_number = flight_number.value,
            aircraft_id = int(aircraft_id.value),
            origin_location_id = int(origin_location_id.value),
            destination_location_id = int(destination_location_id.value),
            departure_gate_id = int(departure_gate_id.value) if departure_gate_id else None,
            arrival_gate_id = int(arrival_gate_id.value) if arrival_gate_id else None,
            captain_id = int(captain_id.value),
            first_officer_id = int(first_officer_id.value),
            scheduled_departure_date = date.fromisoformat(scheduled_departure_date.value),
            scheduled_departure_time = time.fromisoformat(scheduled_departure_time.value),
            scheduled_arrival_date = date.fromisoformat(scheduled_arrival_date.value),
            scheduled_arrival_time = time.fromisoformat(scheduled_arrival_time.value),
            confirmed_departure_date = date.fromisoformat(confirmed_departure_date.value) if len(confirmed_departure_date.value) > 0 else None,
            confirmed_departure_time = time.fromisoformat(confirmed_departure_time.value) if len(confirmed_departure_time.value) > 0 else None,
            confirmed_arrival_date = date.fromisoformat(confirmed_arrival_date.value) if len(confirmed_arrival_date.value) > 0 else None,
            confirmed_arrival_time = time.fromisoformat(confirmed_arrival_time.value) if len(confirmed_arrival_time.value) > 0 else None,
            flight_status = flight_status.value
        )