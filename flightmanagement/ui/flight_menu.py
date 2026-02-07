from datetime import datetime, date, time
from typing import Union, cast
from prompt_toolkit.shortcuts import choice
from flightmanagement.error import FieldValidationError, DomainValidationError, UserCancelled, ConstraintViolation
from flightmanagement.ui.base_menu import BaseMenu, Unset
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.location_service import LocationService
from flightmanagement.models.flight import Flight
from flightmanagement.ui.flight_update_menu import FlightUpdateMenu

class FlightMenu(BaseMenu):

    def __init__(self, session, bindings, conn = None, flight_service = None, aircraft_service = None, location_service = None, pilot_service = None):
        super().__init__(session, bindings, conn)
        
        self._flight_service = flight_service or FlightService(conn)
        self._aircraft_service = aircraft_service or AircraftService(conn)
        self._location_service = location_service or LocationService(conn)
        self._menu_name = "Main -> Manage Flights"
        self._menu_options = [
            ("show", "Show all flights"),
            ("search", "Search flights"),
            ("add", "Add a flight"),
            ("update", "Update a flight"),
            ("delete", "Delete a flight"),
            ("back", "Back to main menu")
        ]

    def load(self):
        while True:
            _selected_option = choice(message = self._format_title(self._menu_name), options = self._menu_options)

            try:
                if _selected_option == "show":
                    self._show_option()
                elif _selected_option == "search":                
                    self._search_option()
                elif _selected_option == "add":
                    self._add_option()
                elif _selected_option == "update":
                    self._update_option()
                elif _selected_option == "delete":
                    self._delete_option()
                elif _selected_option == "back":
                    return
            except UserCancelled as e:
                print(e)
                continue

    def _show_option(self) -> None:
        print("\n>> Displaying all flights\n")
        print(self._flight_service.get_flight_table())

    def _search_option(self) -> None:
        print("\n>> Search for a flight (or hit CTRL+C to cancel)\n")

        flight_number = self._prompt_until_valid(
                prompt_text = "Flight number:",
                getter = lambda p: p.get_str(),
                field = "flight_number"
            )
        result = self._flight_service.search_flights("flight_number", flight_number)
        print(self._format_results_text(len(result), self._flight_service.get_results_view(result)))   

    def _add_option(self) -> None:
        print("\n>> Add a flight (or hit CTRL+C to cancel)\n")

        new = self._prompt_add_flight()        
        new_id = self._flight_service.add_flight(new)
        print(f"\nNew record successfully added (flight ID: {new_id}).\n")

    def _update_option(self) -> None:
        print("\n>> Select a flight to update (or hit CTRL+C to cancel)\n")

        # Prompt for the flight to update
        flight = self._get_flight_from_selection()
        if flight.flight_id is None:
            raise ValueError

        # Load the flight update menu
        FlightUpdateMenu(self._session, self._key_bindings, flight.flight_id, self._conn).load()

    def _delete_option(self) -> None:
        print("\n>> Delete a flight (or hit CTRL+C to cancel)\n")

        # Prompt for the flight to delete
        flight = self._prompt_delete_flight()
        
        # Delete the flight
        try:
            self._flight_service.delete_flight(flight)
            print("\nRecord successfully deleted.\n")
        except ConstraintViolation as e:
            print("\nError deleting flight: the flight still has related records.")
    
    def _prompt_add_flight(self) -> Flight:

        unset = Unset()

        flight_number: Union[str, None, Unset] = unset
        aircraft_id: Union[int, None, Unset] = unset
        origin_location_id: Union[int, None, Unset] = unset
        destination_location_id: Union[int, None, Unset] = unset
        captain_id: Union[int, None, Unset] = unset
        first_officer_id: Union[int, None, Unset] = unset
        scheduled_departure_date: Union[date, None, Unset] = unset
        scheduled_departure_time: Union[time, None, Unset] = unset
        scheduled_arrival_date: Union[date, None, Unset] = unset
        scheduled_arrival_time: Union[time, None, Unset] = unset

        while True:
            try:                

                if flight_number is unset:
                    flight_number = self._prompt_until_valid(
                        prompt_text = "Flight number:",
                        getter = lambda p: p.get_str(),
                        field = "flight_number",
                        required = True
                    )

                if aircraft_id is unset:
                    print()                    
                    aircraft_id = self._prompt_until_valid(
                        prompt_text = "Select an aircraft:",
                        getter = lambda p: p.get_int(),
                        field = "aircraft_id",
                        required = True,
                        is_picklist = True,
                        options = self._aircraft_service.get_aircraft_choices()
                    )                

                if origin_location_id is unset:
                    print()
                    origin_location_id = self._prompt_until_valid(
                        prompt_text = "Select an origin location:",
                        getter = lambda p: p.get_int(),
                        field = "origin_location_id",
                        required = True,
                        is_picklist = True,
                        options = self._location_service.get_location_choices()
                    )             

                if destination_location_id is unset:
                    print()
                    destination_location_id = self._prompt_until_valid(
                        prompt_text = "Select a destination location:",
                        getter = lambda p: p.get_int(),
                        field = "destination_location_id",
                        required = True,
                        is_picklist = True,
                        options = self._location_service.get_location_choices()
                    )    

                if scheduled_departure_date is unset:
                    scheduled_departure_date = self._prompt_until_valid(
                        prompt_text = "Scheduled departure date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_departure_date",
                        required = True
                    )        

                if scheduled_departure_time is unset:
                    scheduled_departure_time = self._prompt_until_valid(
                        prompt_text = "Scheduled departure time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "scheduled_departure_time",
                        required = True
                    )        

                if scheduled_departure_date is unset or scheduled_departure_date is None:
                    arrival_date_default = ""
                else:
                    arrival_date_default = scheduled_departure_date

                if scheduled_arrival_date is unset:
                    scheduled_arrival_date = self._prompt_until_valid(
                        prompt_text = "Scheduled arrival date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_arrival_date",
                        required = True,
                        default_value = arrival_date_default
                    )        

                if scheduled_arrival_time is unset:
                    scheduled_arrival_time = self._prompt_until_valid(
                        prompt_text = "Scheduled arrival time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "scheduled_arrival_time",
                        required = True
                    )         

                if captain_id is unset:
                    print()
                    captain_id = self._prompt_until_valid(
                        prompt_text = "Select the captain:",
                        getter = lambda p: p.get_int(),
                        field = "captain_id",
                        options = self._flight_service.get_available_pilot_choices(
                            departure_time = datetime.combine(cast(date, scheduled_departure_date), cast(time, scheduled_departure_time)),
                            arrival_time = datetime.combine(cast(date, scheduled_arrival_date), cast(time, scheduled_arrival_time))
                        ),                        
                        is_picklist = True,
                        none_option = True
                    )
                    print()

                if first_officer_id is unset:
                    first_officer_id = self._prompt_until_valid(
                        prompt_text = "Select the first officer:",
                        getter = lambda p: p.get_int(),
                        field = "first_officer_id",
                        options = self._flight_service.get_available_pilot_choices(
                            departure_time = datetime.combine(cast(date, scheduled_departure_date), cast(time, scheduled_departure_time)),
                            arrival_time = datetime.combine(cast(date, scheduled_arrival_date), cast(time, scheduled_arrival_time)),
                            unavailable_pilots = [captain_id] if captain_id is not unset else []
                        ),                        
                        is_picklist = True,
                        none_option = True
                    )
                    print()

                return Flight(
                    flight_number = self._required(flight_number, "flight_number"),
                    aircraft_id = self._required(aircraft_id, "aircraft_id"),
                    origin_location_id = self._required(origin_location_id, "origin_location_id"),
                    destination_location_id = self._required(destination_location_id, "destination_location_id"),
                    captain_id = self._optional(captain_id),
                    first_officer_id = self._optional(first_officer_id),
                    scheduled_departure_date = self._required(scheduled_departure_date, "scheduled_departure_date"),
                    scheduled_departure_time = self._required(scheduled_departure_time, "scheduled_departure_time"),
                    scheduled_arrival_date = self._required(scheduled_arrival_date, "scheduled_arrival_date"),
                    scheduled_arrival_time = self._required(scheduled_arrival_time, "scheduled_arrival_time"),
                    flight_status = "Scheduled"
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "flight_number":
                    flight_number = unset
                elif e.field == "aircraft_id":
                    aircraft_id = unset
                elif e.field == "origin_location_id":
                    origin_location_id = unset
                elif e.field == "destination_location_id":
                    destination_location_id = unset
                elif e.field == "captain_id":
                    captain_id = unset
                elif e.field == "first_officer_id":
                    first_officer_id = unset
                elif e.field == "scheduled_departure_date":
                    scheduled_departure_date = unset
                elif e.field == "scheduled_departure_time":
                    scheduled_departure_time = unset
                elif e.field == "scheduled_arrival_date":
                    scheduled_arrival_date = unset
                elif e.field == "scheduled_arrival_time":
                    scheduled_arrival_time = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                flight_number = unset
                aircraft_id = unset
                origin_location_id = unset
                destination_location_id = unset
                captain_id = unset
                first_officer_id = unset
                scheduled_departure_date = unset
                scheduled_departure_time = unset
                scheduled_arrival_date = unset
                scheduled_arrival_time = unset

    def _prompt_delete_flight(self) -> Flight:

        # Prompt for the flight to delete
        flight = self._get_flight_from_selection()
        print()

        # Delete will be cancelled if the user doesn't confirm
        self._prompt_delete_confirmation()
        
        return flight

    def _get_flight_from_selection(self) -> Flight:

        flight_id = None

        while flight_id is None:
            flight_id = self._prompt_until_valid(
                prompt_text = "Choose a flight:",
                getter = lambda p: p.get_int(),
                field = "flight_id",
                required = True,
                is_picklist = True,
                options = self._flight_service.get_flight_choices()
            )

        flight = self._flight_service.get_flight_by_id(flight_id)

        if flight is None:
            raise ValueError("No flight returned from selection.")
        
        if flight.flight_id is None:
            raise ValueError("Selected flight missing unique identifier.")

        return flight

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