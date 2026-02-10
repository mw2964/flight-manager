import pandas as pd
from datetime import datetime, date, time
from typing import Union, cast
from prompt_toolkit.shortcuts import choice
from flightmanagement.error import FieldValidationError, DomainValidationError, UserCancelled, MissingData, DependentRecords, DuplicateRecord, InvalidData
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
            ("find", "Find and update flights"),
            ("add", "Add a flight"),
            ("back", "Back to main menu")
        ]

    def load(self):
        while True:
            _selected_option = choice(message = self._format_title(self._menu_name), options = self._menu_options)

            try:
                if _selected_option == "find":                
                    self._search_option()
                elif _selected_option == "add":
                    self._add_option()
                elif _selected_option == "back":
                    return
            except UserCancelled as e:
                print(e)
                continue

    def _search_option(self) -> None:
        print()
        selected_search_option = self._prompt_until_valid(
            prompt_text = "Select a search option (or hit CTRL+C to cancel):",
            getter = lambda p: p.get_str(),
            field = "selected_search_option",
            is_picklist = True,
            required = True,
            options = [
                ("full_text", "Full text search"),
                ("flight_id", "Search by ID"),
                ("flight_number", "Search by flight number"),
                ("destination_code", "Search by destination"),
                ("departure_date", "Search by departure date"),
                ("flight_status", "Search by flight status")
            ]
        )
        print()
        if not selected_search_option:
            raise ValueError("Missing search option.")
        self._prompt_find_flights(selected_search_option)
        
    def _add_option(self) -> None:
        print("\n>> Add a flight (or hit CTRL+C to cancel)\n")

        new = self._prompt_add_flight()        
        new_id = self._flight_service.add_flight(new)

        try:
            print(f"\nNew record successfully added:\n")
            self._show_flight_summary(new_id)
        except MissingData as e:
            print("\nRecord insert failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord insert failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord insert failed: invalid information.")

    def _prompt_find_flights(self, option: str) -> None:

        df = None
        results = []

        while True:
            try:
                if option == "flight_id":
                    flight_id = self._prompt_until_valid(
                        prompt_text = "Flight ID:",
                        getter = lambda p: p.get_int(),
                        field = "flight_id"
                    )
                    flight_dict = self._flight_service.get_flight_summary_by_id(self._required(flight_id, "flight_id"))
                    if flight_dict is not None:
                        results = [flight_dict]

                elif option == "flight_number":
                    flight_number = self._prompt_until_valid(
                        prompt_text = "Flight number:",
                        getter = lambda p: p.get_str(),
                        field = "flight_number"
                    )
                    results = self._flight_service.search_flights("flight_number", flight_number)

                elif option == "destination_code":
                    destination_code = self._prompt_until_valid(
                        prompt_text = "Destination airport code (3-letter):",
                        getter = lambda p: p.get_str(),
                        field = "destination_code"
                    )
                    results = self._flight_service.search_flights("destination_location", destination_code)

                elif option == "departure_date":
                    scheduled_departure_date = self._prompt_until_valid(
                        prompt_text = "Departure date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_departure_date"
                    )
                    if scheduled_departure_date is not None:
                        formatted_date = scheduled_departure_date.strftime("%Y-%m-%d")
                        results = self._flight_service.search_flights("scheduled_departure_date", formatted_date)

                elif option == "flight_status":
                    flight_status = self._prompt_until_valid(
                        prompt_text = "Select a flight status:",
                        getter = lambda p: p.get_str(),
                        field = "flight_status",
                        is_picklist = True,
                        options = [
                            ("Scheduled", ("Scheduled")),
                            ("Delayed", ("Delayed")),
                            ("On time", ("On time")),
                            ("Boarding", ("Boarding")),
                            ("Closed", ("Closed")),
                            ("Departed", ("Departed")),
                            ("Arrived", ("Arrived"))
                        ],
                        required = True
                    )
                    print()
                    results = self._flight_service.search_flights("flight_status", flight_status)
                    df = pd.json_normalize(results)

                elif option == "full_text":
                    search_text = self._prompt_until_valid(
                        prompt_text = "Search term:",
                        getter = lambda p: p.get_str(),
                        field = "destination_code"
                    )
                    df = self._flight_service.get_flights_full_text(search_text)

                break
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

        if df is None:
            df = pd.json_normalize(results)

        print(self._format_results_text(len(df.index), self._flight_service.get_results_view(df)))

        if len(df.index) == 0:
            return
        
        if len(df) == 1:
            prompt = "Would you like to edit this flight?"
        else:
            prompt = "Would you like to edit one of these flights?"

        update = self._prompt_until_valid(
            prompt_text = prompt,
            getter = lambda p: p.get_str(),
            field = "update",
            is_picklist = True,
            options = [("no", "no"),("yes", "yes")],
            default_value = "yes"
        )
        print()
        if update == "no":
            return
        
        if len(df.index) > 1:
            # More than one flight in the results, so provide a picklist
            flight_id_list = df['flight_id'].tolist()

            flight = self._get_flight_from_selection(flight_id_list)
            if flight.flight_id is None:
                raise ValueError

            update_flight_id = flight.flight_id
        else:
            # Load the flight update menu
            update_flight_id = int(df.iloc[0]["flight_id"])
        
        FlightUpdateMenu(self._session, self._key_bindings, update_flight_id, self._conn).load()

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
                        options = self._aircraft_service.get_aircraft_choices(active=True)
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
                    print()

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
                    arrival_date_default = None
                else:
                    arrival_date_default = cast(date, scheduled_departure_date).strftime("%d/%m/%Y")

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
                            already_on_flight = [captain_id] if captain_id is not unset else []
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

    def _get_flight_from_selection(self, id_list: list | None = None) -> Flight:

        flight_id = None

        while flight_id is None:
            flight_id = self._prompt_until_valid(
                prompt_text = "Choose a flight:",
                getter = lambda p: p.get_int(),
                field = "flight_id",
                required = True,
                is_picklist = True,
                options = self._flight_service.get_flight_choices(id_list = id_list if id_list else None)
            )

        flight = self._flight_service.get_flight_by_id(flight_id)

        if flight is None:
            raise ValueError("No flight returned from selection.")
        
        if flight.flight_id is None:
            raise ValueError("Selected flight missing unique identifier.")

        return flight
    
    def _show_flight_summary(self, flight_id: int) -> None:        
        results = self._flight_service.search_flights("flight_id", flight_id)
        df = pd.json_normalize(results)

        print(self._flight_service.get_results_view(df))