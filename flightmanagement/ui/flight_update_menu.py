import pandas as pd
from datetime import datetime, date, time
from typing import Union, cast
from prompt_toolkit.shortcuts import choice
from flightmanagement.error import FieldValidationError, DomainValidationError, UserCancelled, MissingData, DependentRecords, DuplicateRecord, InvalidData, FlightNotFound
from flightmanagement.ui.base_menu import BaseMenu, Unset
from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.services.location_service import LocationService
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.models.flight import Flight

class FlightUpdateMenu(BaseMenu):

    def __init__(self, session, bindings, flight_id: int, conn = None, flight_service = None, aircraft_service = None, location_service = None, pilot_service = None):
        super().__init__(session, bindings, conn)
        
        self._flight_service = flight_service or FlightService(conn)
        self._aircraft_service = aircraft_service or AircraftService(conn)
        self._location_service = location_service or LocationService(conn)
        self._flight_id = flight_id
        self._menu_name = "Main -> Manage Flights -> Update flight"
        self._menu_options = [
            ("assign_pilot", "Assign captain and/or first officer"),
            ("manage_relief_pilots", "Manage relief pilots"),
            ("update_aircraft", "Assign or change aircraft"),
            ("update_status", "Update flight status"),
            ("update_scheduled_times", "Update scheduled times"),
            ("log_departure", "Log departure"),
            ("log_arrival", "Log arrival"),
            ("update_all", "Update all flight details"),
            ("back", "Back to flights menu")
        ]

    def load(self):
        
        print(f"\nSelected flight:\n")
        self._show_flight_summary()
        
        while True:            

            flight = self._flight_service.get_flight_by_id(self._flight_id)
            if not flight:
                raise FlightNotFound

            _selected_option = choice(message = self._format_title(self._menu_name + f" {flight.flight_number} (ID: {self._flight_id})"), options = self._menu_options)
            
            try:
                if _selected_option == "assign_pilot":
                    self._assign_pilot_option()
                if _selected_option == "manage_relief_pilots":
                    self._manage_relief_pilots_option()
                elif _selected_option == "update_aircraft":                
                    self._update_aircraft_option()
                elif _selected_option == "update_status":                
                    self._update_status_option()
                elif _selected_option == "update_scheduled_times":
                    self._update_scheduled_times_option()
                elif _selected_option == "log_departure":
                    self._log_departure_option()
                elif _selected_option == "log_arrival":
                    self._log_arrival_option()
                elif _selected_option == "update_all":
                    self._update_all_option()
                elif _selected_option == "back":
                    return
            except UserCancelled as e:
                print(e)
                continue
    
    def _show_flight_summary(self) -> None:        
        results = self._flight_service.search_flights("flight_id", self._flight_id)
        df = pd.json_normalize(results)

        print(self._flight_service.get_results_view(df))

    def _assign_pilot_option(self) -> None:
        print("\n>> Assign a pilot (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_assign_pilot(flight)

        # Update the flight record
        self._flight_service.update_flight(update)
        print("\nFlight details successfully updated:\n")
        self._show_flight_summary()

    def _manage_relief_pilots_option(self) -> None:
        print("\n>> Update relief pilots (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        option = self._prompt_until_valid(
            prompt_text = "What would you like to do?",
            getter = lambda p: p.get_int(),
            field = "option",
            is_picklist = True,
            required = True,
            options = [
                (1, ("Add a relief pilot")),
                (2, ("Remove a relief pilot"))
            ]
        )
        print()

        if option == 1:            
            staff_id = self._prompt_add_relief_pilot(flight)
            self._flight_service.add_relief_pilot(flight, staff_id)
            print("\nRelief pilot successfully added:\n")
            self._show_flight_summary()
        
        elif option == 2:
            staff_id = self._prompt_remove_relief_pilot(flight)
            if staff_id:
                self._flight_service.remove_relief_pilot(flight, staff_id)
                print("\nRelief pilot successfully removed:\n")
                self._show_flight_summary()

    def _update_aircraft_option(self) -> None:
        print("\n>> Update the aircraft (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_update_aircraft(flight)

        try:
            self._flight_service.update_flight(update)
            print("\nAircraft successfully updated:\n")
            self._show_flight_summary()
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")
        
    def _update_status_option(self) -> None:
        print("\n>> Update the flight status (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_update_status(flight)

        try:
            self._flight_service.update_flight(update)
            print("\nStatus successfully updated:\n")
            self._show_flight_summary()
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")

    def _update_scheduled_times_option(self) -> None:
        print("\n>> Update the scheduled departure and arrival times (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_update_scheduled_times(flight)

        try:
            self._flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self._show_flight_summary()
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")

    def _log_departure_option(self) -> None:
        print("\n>> Log the actual departure time and set status to 'departed' (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_log_departure(flight)

        try:
            self._flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self._show_flight_summary()
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")
    
    def _log_arrival_option(self) -> None:
        print("\n>> Log the actual arrival time and set status to 'arrived' (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_log_arrival(flight)

        try:
            self._flight_service.update_flight(update)
            print("\nFlight details successfully updated:\n")
            self._show_flight_summary()
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")

    def _update_all_option(self) -> None:
        print("\n>> Update a flight (or hit CTRL+C to cancel)\n")

        flight = self._flight_service.get_flight_by_id(self._flight_id)
        if flight is None:
            raise FlightNotFound

        # Prompt the user to edit fields
        update = self._prompt_update_flight(flight)

        try:
            self._flight_service.update_flight(update)
            print("\nFlight details successfully updated.\n")
            self._show_flight_summary()
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")
        
    def _prompt_log_departure(self, flight: Flight) -> Flight:

        unset = Unset()

        confirmed_departure_date: Union[date, None, Unset] = unset
        confirmed_departure_time: Union[time, None, Unset] = unset

        while True:
            try:            
                if confirmed_departure_date is unset:
                    confirmed_departure_date = self._prompt_until_valid(
                        prompt_text = "Confirmed departure date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "confirmed_departure_date",
                        required = True,
                        default_value = flight.scheduled_departure_date.strftime("%d/%m/%Y")
                    )     

                if confirmed_departure_time is unset:
                    confirmed_departure_time = self._prompt_until_valid(
                        prompt_text = "Confirmed departure time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "confirmed_departure_time",
                        required = True,
                        default_value = flight.scheduled_departure_time.strftime("%H:%M")
                    )        

                return Flight(
                    flight_id = flight.flight_id,
                    flight_number = flight.flight_number,
                    aircraft_id = flight.aircraft_id,
                    origin_location_id = flight.origin_location_id,
                    destination_location_id = flight.destination_location_id,
                    departure_gate_id = flight.departure_gate_id,
                    arrival_gate_id = flight.arrival_gate_id,
                    captain_id = flight.captain_id,
                    first_officer_id = flight.first_officer_id,
                    scheduled_departure_date = flight.scheduled_departure_date,
                    scheduled_departure_time = flight.scheduled_departure_time,
                    scheduled_arrival_date = flight.scheduled_arrival_date,
                    scheduled_arrival_time = flight.scheduled_arrival_time,
                    confirmed_departure_date = self._required(confirmed_departure_date, "confirmed_departure_date"),
                    confirmed_departure_time = self._required(confirmed_departure_time, "confirmed_departure_time"),
                    confirmed_arrival_date = flight.confirmed_arrival_date,
                    confirmed_arrival_time = flight.confirmed_arrival_time,
                    flight_status = "Departed"
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "confirmed_departure_date":
                    confirmed_departure_date = unset
                elif e.field == "confirmed_departure_time":
                    confirmed_departure_time = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                confirmed_departure_date = unset
                confirmed_departure_time = unset

    def _prompt_update_scheduled_times(self, flight: Flight) -> Flight:

        unset = Unset()

        scheduled_departure_date: Union[date, None, Unset] = unset
        scheduled_departure_time: Union[time, None, Unset] = unset
        scheduled_arrival_date: Union[date, None, Unset] = unset
        scheduled_arrival_time: Union[time, None, Unset] = unset

        while True:
            try:            
                if scheduled_departure_date is unset:
                    scheduled_departure_date = self._prompt_until_valid(
                        prompt_text = "Scheduled departure date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_departure_date",
                        required = True,
                        default_value = flight.scheduled_departure_date.strftime("%d/%m/%Y")
                    )     

                if scheduled_departure_time is unset:
                    scheduled_departure_time = self._prompt_until_valid(
                        prompt_text = "Scheduled departure time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "scheduled_departure_time",
                        required = True,
                        default_value = flight.scheduled_departure_time.strftime("%H:%M")
                    )
                
                if scheduled_arrival_date is unset:
                    scheduled_arrival_date = self._prompt_until_valid(
                        prompt_text = "Scheduled arrival date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_arrival_date",
                        required = True,
                        default_value = flight.scheduled_arrival_date.strftime("%d/%m/%Y")
                    )     

                if scheduled_arrival_time is unset:
                    scheduled_arrival_time = self._prompt_until_valid(
                        prompt_text = "Scheduled arrival time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "scheduled_arrival_time",
                        required = True,
                        default_value = flight.scheduled_arrival_time.strftime("%H:%M")
                    )

                return Flight(
                    flight_id = flight.flight_id,
                    flight_number = flight.flight_number,
                    aircraft_id = flight.aircraft_id,
                    origin_location_id = flight.origin_location_id,
                    destination_location_id = flight.destination_location_id,
                    departure_gate_id = flight.departure_gate_id,
                    arrival_gate_id = flight.arrival_gate_id,
                    captain_id = flight.captain_id,
                    first_officer_id = flight.first_officer_id,
                    scheduled_departure_date = self._required(scheduled_departure_date, "scheduled_departure_date"),
                    scheduled_departure_time = self._required(scheduled_departure_time, "scheduled_departure_time"),
                    scheduled_arrival_date = self._required(scheduled_arrival_date, "scheduled_arrival_date"),
                    scheduled_arrival_time = self._required(scheduled_arrival_time, "scheduled_arrival_time"),
                    confirmed_departure_date = flight.confirmed_departure_date,
                    confirmed_departure_time = flight.confirmed_departure_time,
                    confirmed_arrival_date = flight.confirmed_arrival_date,
                    confirmed_arrival_time = flight.confirmed_arrival_time,
                    flight_status = "Departed"
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "scheduled_departure_date":
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

                scheduled_departure_date = unset
                scheduled_departure_time = unset
                scheduled_arrival_date = unset
                scheduled_arrival_time = unset

    def _prompt_log_arrival(self, flight: Flight) -> Flight:

        unset = Unset()

        confirmed_arrival_date: Union[date, None, Unset] = unset
        confirmed_arrival_time: Union[time, None, Unset] = unset

        while True:
            try:            
                if confirmed_arrival_date is unset:
                    confirmed_arrival_date = self._prompt_until_valid(
                        prompt_text = "Confirmed arrival date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "confirmed_arrival_date",
                        required = True,
                        default_value = flight.scheduled_arrival_date.strftime("%d/%m/%Y")
                    )     

                if confirmed_arrival_time is unset:
                    confirmed_arrival_time = self._prompt_until_valid(
                        prompt_text = "Confirmed arrival time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "confirmed_arrival_time",
                        required = True,
                        default_value = flight.scheduled_arrival_time.strftime("%H:%M")
                    )        

                return Flight(
                    flight_id = flight.flight_id,
                    flight_number = flight.flight_number,
                    aircraft_id = flight.aircraft_id,
                    origin_location_id = flight.origin_location_id,
                    destination_location_id = flight.destination_location_id,
                    departure_gate_id = flight.departure_gate_id,
                    arrival_gate_id = flight.arrival_gate_id,
                    captain_id = flight.captain_id,
                    first_officer_id = flight.first_officer_id,
                    scheduled_departure_date = flight.scheduled_departure_date,
                    scheduled_departure_time = flight.scheduled_departure_time,
                    scheduled_arrival_date = flight.scheduled_arrival_date,
                    scheduled_arrival_time = flight.scheduled_arrival_time,
                    confirmed_departure_date = flight.confirmed_departure_date,
                    confirmed_departure_time = flight.confirmed_departure_time,
                    confirmed_arrival_date = self._required(confirmed_arrival_date, "confirmed_arrival_date"),
                    confirmed_arrival_time = self._required(confirmed_arrival_time, "confirmed_arrival_time"),
                    flight_status = "Arrived"
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "confirmed_arrival_date":
                    confirmed_arrival_date = unset
                elif e.field == "confirmed_arrival_time":
                    confirmed_arrival_time = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                confirmed_arrival_date = unset
                confirmed_arrival_time = unset

    def _prompt_update_status(self, flight: Flight) -> Flight:

        unset = Unset()

        flight_status: Union[str, None, Unset] = unset

        while True:
            try:            
                if flight_status is unset:
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
                        default_value = flight.flight_status,
                        required = True
                    )
                    print()

                return Flight(
                    flight_id = flight.flight_id,
                    flight_number = flight.flight_number,
                    aircraft_id = flight.aircraft_id,
                    origin_location_id = flight.origin_location_id,
                    destination_location_id = flight.destination_location_id,
                    departure_gate_id = flight.departure_gate_id,
                    arrival_gate_id = flight.arrival_gate_id,
                    captain_id = flight.captain_id,
                    first_officer_id = flight.first_officer_id,
                    scheduled_departure_date = flight.scheduled_departure_date,
                    scheduled_departure_time = flight.scheduled_departure_time,
                    scheduled_arrival_date = flight.scheduled_arrival_date,
                    scheduled_arrival_time = flight.scheduled_arrival_time,
                    confirmed_departure_date = flight.confirmed_departure_date,
                    confirmed_departure_time = flight.confirmed_departure_time,
                    confirmed_arrival_date = flight.confirmed_arrival_date,
                    confirmed_arrival_time = flight.confirmed_arrival_time,
                    flight_status = self._required(flight_status, "flight_status")
                )
            
            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "flight_status":
                    flight_status = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                flight_status = unset

    def _prompt_update_aircraft(self, flight: Flight) -> Flight:

        unset = Unset()

        aircraft_id: Union[int, None, Unset] = unset

        while True:
            try:

                if aircraft_id is unset:
                    aircraft_id = self._prompt_until_valid(
                        prompt_text = "Select an aircraft:",
                        getter = lambda p: p.get_int(),
                        field = "aircraft_id",
                        is_picklist = True,
                        none_option = True,
                        options = self._aircraft_service.get_aircraft_choices(),
                        default_value = flight.aircraft_id
                    )
                    print()

                return Flight(
                    flight_id = flight.flight_id,
                    flight_number = flight.flight_number,
                    aircraft_id = self._optional(aircraft_id),
                    origin_location_id = flight.origin_location_id,
                    destination_location_id = flight.destination_location_id,
                    departure_gate_id = flight.departure_gate_id,
                    arrival_gate_id = flight.arrival_gate_id,
                    captain_id = flight.captain_id,
                    first_officer_id = flight.first_officer_id,
                    scheduled_departure_date = flight.scheduled_departure_date,
                    scheduled_departure_time = flight.scheduled_departure_time,
                    scheduled_arrival_date = flight.scheduled_arrival_date,
                    scheduled_arrival_time = flight.scheduled_arrival_time,
                    confirmed_departure_date = flight.confirmed_departure_date,
                    confirmed_departure_time = flight.confirmed_departure_time,
                    confirmed_arrival_date = flight.confirmed_arrival_date,
                    confirmed_arrival_time = flight.confirmed_arrival_time,
                    flight_status = flight.flight_status
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "aircraft_id":
                    aircraft_id = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                aircraft_id = unset

    def _prompt_assign_pilot(self, flight: Flight) -> Flight:

        unset = Unset()

        captain_id: Union[int, None, Unset] = unset
        first_officer_id: Union[int, None, Unset] = unset

        while True:
            try:

                # Initialise the unavailable pilots list from any currently assigned refief pilots
                excluded_pilots = self._flight_service.get_flight_relief_pilots(flight)

                if captain_id is unset:
                    captain_id  = self._prompt_until_valid(
                        prompt_text = "Select a captain:",
                        getter = lambda p: p.get_int(),
                        field = "captain_id",
                        is_picklist = True,
                        none_option = True,
                        options = self._flight_service.get_available_pilot_choices(
                            departure_time = datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                            arrival_time = datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                            flight_id = flight.flight_id,
                            unavailable_pilots = excluded_pilots
                        ),
                        default_value = flight.captain_id
                    )
                    print()

                # Add the captain to the excluded pilots list
                excluded_pilots.append(captain_id) if captain_id is not None and captain_id is not unset else flight.captain_id

                if first_officer_id is unset:
                    first_officer_id = self._prompt_until_valid(
                        prompt_text = "Select a first officer:",
                        getter = lambda p: p.get_int(),
                        field = "first_officer_id",
                        is_picklist = True,
                        none_option = True,
                        options = self._flight_service.get_available_pilot_choices(
                            departure_time = datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                            arrival_time = datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                            flight_id = flight.flight_id,
                            unavailable_pilots = excluded_pilots
                        ),
                        default_value = flight.first_officer_id
                    )
                    print()

                    return Flight(
                        flight_id = flight.flight_id,
                        flight_number = flight.flight_number,
                        aircraft_id = flight.aircraft_id,
                        origin_location_id = flight.origin_location_id,
                        destination_location_id = flight.destination_location_id,
                        departure_gate_id = flight.departure_gate_id,
                        arrival_gate_id = flight.arrival_gate_id,
                        captain_id = self._optional(captain_id),
                        first_officer_id = self._optional(first_officer_id),
                        scheduled_departure_date = flight.scheduled_departure_date,
                        scheduled_departure_time = flight.scheduled_departure_time,
                        scheduled_arrival_date = flight.scheduled_arrival_date,
                        scheduled_arrival_time = flight.scheduled_arrival_time,
                        confirmed_departure_date = flight.confirmed_departure_date,
                        confirmed_departure_time = flight.confirmed_departure_time,
                        confirmed_arrival_date = flight.confirmed_arrival_date,
                        confirmed_arrival_time = flight.confirmed_arrival_time,
                        flight_status = flight.flight_status
                    )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "captain_id":
                    captain_id = unset
                elif e.field == "first_officer_id":
                    first_officer_id = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                captain_id = unset
                first_officer_id = unset

    def _prompt_remove_relief_pilot(self, flight: Flight) -> int | None:
        
        choices = self._flight_service.get_flight_relief_pilot_choices(flight)
        if len(choices) == 0:
            print("\nNo relief pilots currently assigned to this flight.\n")
            return None
        
        staff_id = self._prompt_until_valid(
            prompt_text = "Select the pilot to remove:",
            getter = lambda p: p.get_int(),
            field = "staff_id",
            is_picklist = True,
            options = choices
        )
        print()

        return staff_id
    
    def _prompt_add_relief_pilot(self, flight: Flight) -> int:
        
        # Exclude any currently assigned relief pilots, captain and first officer from the available options
        excluded_pilots = self._flight_service.get_flight_relief_pilots(flight)
        
        if flight.captain_id is not None:
            excluded_pilots.append(flight.captain_id)
        if flight.first_officer_id is not None:
            excluded_pilots.append(flight.first_officer_id)

        staff_id = self._prompt_until_valid(
            prompt_text = "Select the pilot to assign:",
            getter = lambda p: p.get_int(),
            field = "staff_id",
            is_picklist = True,
            options = self._flight_service.get_available_pilot_choices(
                    departure_time = datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                    arrival_time = datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                    flight_id = flight.flight_id,
                    unavailable_pilots = excluded_pilots
                )
        )
        print()

        return self._required(staff_id, "staff_id")

    def _prompt_update_flight(self, flight: Flight) -> Flight:

        unset = Unset()

        flight_number: Union[str, None, Unset] = unset
        aircraft_id: Union[int, None, Unset] = unset
        origin_location_id: Union[int, None, Unset] = unset
        destination_location_id: Union[int, None, Unset] = unset
        departure_gate_id: Union[int, None, Unset] = unset
        arrival_gate_id: Union[int, None, Unset] = unset
        captain_id: Union[int, None, Unset] = unset
        first_officer_id: Union[int, None, Unset] = unset
        scheduled_departure_date: Union[date, None, Unset] = unset
        scheduled_departure_time: Union[time, None, Unset] = unset
        scheduled_arrival_date: Union[date, None, Unset] = unset
        scheduled_arrival_time: Union[time, None, Unset] = unset
        confirmed_departure_date: Union[date, None, Unset] = unset
        confirmed_departure_time: Union[time, None, Unset] = unset
        confirmed_arrival_date: Union[date, None, Unset] = unset
        confirmed_arrival_time: Union[time, None, Unset] = unset
        flight_status: Union[str, None, Unset] = unset

        while True:
            try:     

                if flight_number is unset:
                    flight_number = self._prompt_until_valid(
                        prompt_text = "Flight number:",
                        getter = lambda p: p.get_str(),
                        field = "flight_number",
                        required = True,
                        default_value = flight.flight_number
                    )
                
                if aircraft_id is unset:
                    print()                    
                    aircraft_id = self._prompt_until_valid(
                        prompt_text = "Select an aircraft:",
                        getter = lambda p: p.get_int(),
                        field = "aircraft_id",
                        required = True,
                        is_picklist = True,
                        options = self._aircraft_service.get_aircraft_choices(),
                        default_value = flight.aircraft_id
                    )                

                if origin_location_id is unset:
                    print()
                    origin_location_id = self._prompt_until_valid(
                        prompt_text = "Select an origin location:",
                        getter = lambda p: p.get_int(),
                        field = "origin_location_id",
                        required = True,
                        is_picklist = True,
                        options = self._location_service.get_location_choices(),
                        default_value = flight.origin_location_id
                    )        

                if destination_location_id is unset:
                    print()
                    destination_location_id = self._prompt_until_valid(
                        prompt_text = "Select a destination location:",
                        getter = lambda p: p.get_int(),
                        field = "destination_location_id",
                        required = True,
                        is_picklist = True,
                        options = self._location_service.get_location_choices(),
                        default_value = flight.destination_location_id
                    )
                    print()

                if scheduled_departure_date is unset:
                    scheduled_departure_date = self._prompt_until_valid(
                        prompt_text = "Scheduled departure date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_departure_date",
                        required = True,
                        default_value = flight.scheduled_departure_date.strftime("%d/%m/%Y")
                    )    

                if scheduled_departure_time is unset:
                    scheduled_departure_time = self._prompt_until_valid(
                        prompt_text = "Scheduled departure time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "scheduled_departure_time",
                        required = True,
                        default_value = flight.scheduled_departure_time.strftime("%H:%M")
                    )    

                if scheduled_arrival_date is unset:
                    scheduled_arrival_date = self._prompt_until_valid(
                        prompt_text = "Scheduled arrival date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "scheduled_arrival_date",
                        required = True,
                        default_value = flight.scheduled_arrival_date.strftime("%d/%m/%Y")
                    )

                if scheduled_arrival_time is unset:
                    scheduled_arrival_time = self._prompt_until_valid(
                        prompt_text = "Scheduled arrival time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "scheduled_arrival_time",
                        required = True,
                        default_value = flight.scheduled_arrival_time.strftime("%H:%M")
                    )      

                excluded_pilots = self._flight_service.get_flight_relief_pilots(flight)

                if captain_id is unset:
                    print()
                    captain_id = self._prompt_until_valid(
                        prompt_text = "Select the captain:",
                        getter = lambda p: p.get_int(),
                        field = "captain_id",
                        is_picklist = True,
                        none_option = True,
                        options = self._flight_service.get_available_pilot_choices(
                            departure_time = datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                            arrival_time = datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                            flight_id = flight.flight_id,
                            unavailable_pilots = excluded_pilots
                        ),
                        default_value = flight.captain_id if flight.captain_id is not None else -1
                    )
                    print()

                # Add the captain to the excluded pilots list
                excluded_pilots.append(captain_id) if captain_id is not None and captain_id is not unset else flight.captain_id

                if first_officer_id is unset:
                    first_officer_id = self._prompt_until_valid(
                        prompt_text = "Select the first officer:",
                        getter = lambda p: p.get_int(),
                        field = "first_officer_id",
                        options = self._flight_service.get_available_pilot_choices(
                            departure_time = datetime.combine(flight.scheduled_departure_date, flight.scheduled_departure_time),
                            arrival_time = datetime.combine(flight.scheduled_arrival_date, flight.scheduled_arrival_time),
                            flight_id = flight.flight_id,
                            unavailable_pilots = excluded_pilots
                        ),
                        default_value = flight.first_officer_id if flight.first_officer_id is not None else -1,
                        is_picklist = True,
                        none_option = True
                    )
                    print()

                origin_location = self._location_service.get_location_by_id(cast(int, origin_location_id))
                origin_name = origin_location.location_name if origin_location else ""

                if departure_gate_id is unset:
                    departure_gate_id = self._prompt_until_valid(
                        prompt_text = f"Select the departure gate ({origin_name}):",
                        getter = lambda p: p.get_int(),
                        field = "departure_gate_id",
                        is_picklist = True,
                        none_option = True,
                        options = self._location_service.get_airport_gate_choices(cast(int, origin_location_id)),
                        default_value = flight.departure_gate_id
                    )
                    print()

                if confirmed_departure_date is unset:
                    confirmed_departure_date = self._prompt_until_valid(
                        prompt_text = "Confirmed departure date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "confirmed_departure_date",
                        default_value = flight.confirmed_departure_date.strftime("%d/%m/%Y") if flight.confirmed_departure_date else None
                    )    

                if confirmed_departure_time is unset:
                    confirmed_departure_time = self._prompt_until_valid(
                        prompt_text = "Confirmed departure time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "confirmed_departure_time",
                        default_value = flight.confirmed_departure_time.strftime("%H:%M") if flight.confirmed_departure_time else None
                    )    

                destination_location = self._location_service.get_location_by_id(cast(int, destination_location_id))
                destination_name = destination_location.location_name if destination_location else ""

                if arrival_gate_id is unset:
                    arrival_gate_id = self._prompt_until_valid(
                        prompt_text = f"Select the arrival gate ({destination_name}):",
                        getter = lambda p: p.get_int(),
                        field = "arrival_gate_id",
                        is_picklist = True,
                        none_option = True,
                        options = self._location_service.get_airport_gate_choices(cast(int, destination_location_id)),
                        default_value = flight.arrival_gate_id
                    )
                    print()

                if confirmed_arrival_date is unset:
                    confirmed_arrival_date = self._prompt_until_valid(
                        prompt_text = "Confirmed arrival date (DD/MM/YYYY):",
                        getter = lambda p: p.get_date(),
                        field = "confirmed_arrival_date",
                        default_value = flight.confirmed_arrival_date.strftime("%d/%m/%Y") if flight.confirmed_arrival_date else None
                    )    

                if confirmed_arrival_time is unset:
                    confirmed_arrival_time = self._prompt_until_valid(
                        prompt_text = "Confirmed arrival time (HH:MM):",
                        getter = lambda p: p.get_time(),
                        field = "confirmed_arrival_time",
                        default_value = flight.confirmed_arrival_time.strftime("%H:%M") if flight.confirmed_arrival_time else None
                    )    

                if flight_status is unset:
                    print()
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
                        default_value = flight.flight_status,
                        required = True
                    )
                    print()

                return Flight(
                    flight_id = flight.flight_id,
                    flight_number = self._required(flight_number, "flight_number"),
                    aircraft_id = self._optional(aircraft_id),
                    origin_location_id = self._required(origin_location_id, "origin_location_id"),
                    destination_location_id = self._required(destination_location_id, "destination_location_id"),
                    departure_gate_id = self._optional(departure_gate_id),
                    arrival_gate_id = self._optional(arrival_gate_id),
                    captain_id = self._optional(captain_id),
                    first_officer_id = self._optional(first_officer_id),
                    scheduled_departure_date = self._required(scheduled_departure_date, "scheduled_departure_date"),
                    scheduled_departure_time = self._required(scheduled_departure_time, "scheduled_departure_time"),
                    scheduled_arrival_date = self._required(scheduled_arrival_date, "scheduled_arrival_date"),
                    scheduled_arrival_time = self._required(scheduled_arrival_time, "scheduled_arrival_time"),
                    confirmed_departure_date = self._optional(confirmed_departure_date),
                    confirmed_departure_time = self._optional(confirmed_departure_time),
                    confirmed_arrival_date = self._optional(confirmed_arrival_date),
                    confirmed_arrival_time = self._optional(confirmed_arrival_time),
                    flight_status = self._required(flight_status, "flight_status")
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
                elif e.field == "departure_gate_id":
                    departure_gate_id = unset
                elif e.field == "arrival_gate_id":
                    arrival_gate_id = unset    
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
                elif e.field == "confirmed_departure_date":
                    confirmed_departure_date = unset
                elif e.field == "confirmed_departure_time":
                    confirmed_departure_time = unset
                elif e.field == "confirmed_arrival_date":
                    confirmed_arrival_date = unset
                elif e.field == "confirmed_arrival_time":
                    confirmed_arrival_time = unset
                elif e.field == "flight_status":
                    flight_status = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                flight_number = unset
                aircraft_id = unset
                origin_location_id = unset
                destination_location_id = unset
                departure_gate_id = unset
                arrival_gate_id = unset
                captain_id = unset
                first_officer_id = unset
                scheduled_departure_date = unset
                scheduled_departure_time = unset
                scheduled_arrival_date = unset
                scheduled_arrival_time = unset
                confirmed_departure_date = unset
                confirmed_departure_time = unset
                confirmed_arrival_date = unset
                confirmed_arrival_time = unset
                flight_status = unset