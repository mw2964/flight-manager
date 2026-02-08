from prompt_toolkit.shortcuts import choice
from typing import Union
from flightmanagement.error import FieldValidationError, DomainValidationError, UserCancelled, MissingData, DependentRecords, DuplicateRecord, InvalidData
from flightmanagement.ui.base_menu import BaseMenu, Unset
from flightmanagement.services.location_service import LocationService
from flightmanagement.models.location import Location

class LocationMenu(BaseMenu):

    def __init__(self, session, bindings, conn = None, location_service = None):
        super().__init__(session, bindings, conn)

        self._location_service = location_service or LocationService(conn)
        self._menu_name = "Main -> Manage Destinations"
        self._menu_options = [
            ("show", "Show all destinations"),
            ("search", "Search destinations"),
            ("add", "Add a destination"),
            ("update", "Update a destination"),
            ("delete", "Remove a destination"),
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
        print("\n>> Displaying all destinations\n")
        print(self._location_service.get_location_table())

    def _search_option(self) -> None:
        print("\n>> Search for a destination (or hit CTRL+C to cancel)\n")

        iata_airport_code = self._prompt_until_valid(
            prompt_text = "Airport code:",
            getter = lambda p: p.get_str(),
            field = "iata_airport_code",
            required = True
        )
        result = self._location_service.search_locations("iata_airport_code", iata_airport_code)
        print(self._format_results_text(len(result), self._location_service.get_results_view(result)))

    def _add_option(self) -> None:
        print("\n>> Add a destination (or hit CTRL+C to cancel)\n")

        new = self._prompt_add_location()

        try:
            new_id = self._location_service.add_location(new)
            print(f"\nNew record successfully added (Location ID {new_id}).\n")
        except MissingData as e:
            print("\nRecord insert failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord insert failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord insert failed: invalid information.")

    def _update_option(self) -> None:
        print("\n>> Update a destination (or hit CTRL+C to cancel)\n")

        # Prompt for the location to edit
        location = self._get_location_from_selection()
        print(f"\nEditing information (location ID {location.location_id})\n")

        update = self._prompt_update_location(location)

        try:
            self._location_service.update_location(update)
            print("\nRecord successfully updated.\n")
        except MissingData as e:
            print("\nRecord update failed: missing mandatory data.")
        except DuplicateRecord as e:
            print("\nRecord update failed: duplicated information.")
        except InvalidData as e:
            print("\nRecord update failed: invalid information.")

    def _delete_option(self) -> None:
        print("\n>> Delete a destination (or hit CTRL+C to cancel)\n")

        # Prompt for the location to delete
        location = self._prompt_delete_location()
        
        # Delete the aircraft
        try:
            self._location_service.delete_location(location)
            print("\nRecord successfully deleted.\n")
        except DependentRecords as e:
            print("\nCannot delete destination while there are still related flight records.")

    def _prompt_add_location(self) -> Location:

        unset = Unset()

        location_type: Union[str, None, Unset] = unset
        location_name: Union[str, None, Unset] = unset
        iata_airport_code: Union[str, None, Unset] = unset
        icao_location_code: Union[str, None, Unset] = unset
        town_or_city: Union[str, None, Unset] = unset
        state_or_county: Union[str, None, Unset] = unset
        country: Union[str, None, Unset] = unset
        geographic_region: Union[str, None, Unset] = unset
        decimal_latitude: Union[float, None, Unset] = unset
        decimal_longitude: Union[float, None, Unset] = unset

        while True:
            try:
                if location_type is unset:
                    location_type = self._prompt_until_valid(
                        prompt_text="Select a location type:",
                        getter = lambda p: p.get_str(),
                        field = "location_type",
                        required = True,
                        is_picklist=True,
                        options=[
                            ("Airport", ("Airport")),
                            ("Airfield", ("Airfield"))
                        ],
                        default_value = "Airport"
                    )
                    print()

                if iata_airport_code is unset:
                    iata_airport_code = self._prompt_until_valid(
                        prompt_text = "Airport code (3-character):",
                        getter = lambda p: p.get_str(),
                        field = "iata_airport_code"
                    )
                    
                if icao_location_code is unset:
                    icao_location_code = self._prompt_until_valid(
                        prompt_text = "ICAO location code (4-character):",
                        getter = lambda p: p.get_str(),
                        field = "icao_location_code"
                    )
                    
                if location_name is unset:
                    location_name = self._prompt_until_valid(
                        prompt_text = "Name of the airport (or other type of location):",
                        getter = lambda p: p.get_str(),
                        field = "location_name",
                        required = True
                    )

                if town_or_city is unset:
                    town_or_city = self._prompt_until_valid(
                        prompt_text = "Town/city:",
                        getter = lambda p: p.get_str(),
                        field = "town_or_city"
                    )

                if state_or_county is unset:
                    state_or_county = self._prompt_until_valid(
                        prompt_text = "State/county/province:",
                        getter = lambda p: p.get_str(),
                        field = "state_or_county"
                    )

                if country is unset:
                    country = self._prompt_until_valid(
                        prompt_text = "Country:",
                        getter = lambda p: p.get_str(),
                        field = "country",
                        required = True
                    )

                if geographic_region is unset:
                    geographic_region = self._prompt_until_valid(
                        prompt_text = "Wider geographic region:",
                        getter = lambda p: p.get_str(),
                        field = "geographic_region"
                    )

                if decimal_latitude is unset:
                    decimal_latitude = self._prompt_until_valid(
                        prompt_text = "Latitude (decimal):",
                        getter = lambda p: p.get_float(),
                        field = "decimal_latitude"
                    )

                if decimal_longitude is unset:
                    decimal_longitude = self._prompt_until_valid(
                        prompt_text = "Longitude (decimal):",
                        getter = lambda p: p.get_float(),
                        field = "decimal_longitude"
                    )

                return Location(
                    location_type = self._required(location_type, "location_type"),
                    iata_airport_code = self._optional(iata_airport_code),
                    icao_location_code = self._optional(icao_location_code),
                    location_name = self._required(location_name, "location_name"),
                    town_or_city = self._optional(town_or_city),
                    state_or_county = self._optional(state_or_county),
                    country = self._required(country, "country"),
                    geographic_region = self._optional(geographic_region),
                    decimal_latitude = self._optional(decimal_latitude),
                    decimal_longitude = self._optional(decimal_longitude)
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "location_type":
                    location_type = unset
                elif e.field == "location_name":
                    location_name = unset
                elif e.field == "iata_airport_code":
                    iata_airport_code = unset
                elif e.field == "icao_location_code":
                    icao_location_code = unset
                elif e.field == "town_or_city":
                    town_or_city = unset
                elif e.field == "state_or_county":
                    state_or_county = unset
                elif e.field == "country":
                    country = unset
                elif e.field == "geographic_region":
                    geographic_region = unset
                elif e.field == "decimal_latitude":
                    decimal_latitude = unset
                elif e.field == "decimal_longitude":
                    decimal_longitude = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                location_type = unset
                location_name = unset
                iata_airport_code = unset
                icao_location_code = unset
                town_or_city = unset
                state_or_county = unset
                country = unset
                geographic_region = unset
                decimal_latitude = unset
                decimal_longitude = unset

    def _prompt_update_location(self, location: Location) -> Location:

        unset = Unset()

        location_type: Union[str, None, Unset] = unset
        location_name: Union[str, None, Unset] = unset
        iata_airport_code: Union[str, None, Unset] = unset
        icao_location_code: Union[str, None, Unset] = unset
        town_or_city: Union[str, None, Unset] = unset
        state_or_county: Union[str, None, Unset] = unset
        country: Union[str, None, Unset] = unset
        geographic_region: Union[str, None, Unset] = unset
        decimal_latitude: Union[float, None, Unset] = unset
        decimal_longitude: Union[float, None, Unset] = unset

        while True:
            try:
                if location_type is unset:
                    location_type = self._prompt_until_valid(
                        prompt_text="Select a location type:",
                        getter = lambda p: p.get_str(),
                        field = "location_type",
                        required = True,
                        is_picklist=True,
                        options=[
                            ("Airport", ("Airport")),
                            ("Airfield", ("Airfield"))
                        ],
                        default_value = location.location_type
                    )
                    print()

                if iata_airport_code is unset:
                    iata_airport_code = self._prompt_until_valid(
                        prompt_text = "Airport code (3-character):",
                        getter = lambda p: p.get_str(),
                        field = "iata_airport_code",
                        default_value = location.iata_airport_code
                    )
                    
                if icao_location_code is unset:
                    icao_location_code = self._prompt_until_valid(
                        prompt_text = "ICAO location code (4-character):",
                        getter = lambda p: p.get_str(),
                        field = "icao_location_code",
                        default_value = location.icao_location_code
                    )
                    
                if location_name is unset:
                    location_name = self._prompt_until_valid(
                        prompt_text = "Name of the airport (or other type of location):",
                        getter = lambda p: p.get_str(),
                        field = "location_name",
                        required = True,
                        default_value = location.location_name
                    )

                if town_or_city is unset:
                    town_or_city = self._prompt_until_valid(
                        prompt_text = "Town/city:",
                        getter = lambda p: p.get_str(),
                        field = "town_or_city",
                        default_value = location.town_or_city
                    )

                if state_or_county is unset:
                    state_or_county = self._prompt_until_valid(
                        prompt_text = "State/county/province:",
                        getter = lambda p: p.get_str(),
                        field = "state_or_county",
                        default_value = location.state_or_county
                    )

                if country is unset:
                    country = self._prompt_until_valid(
                        prompt_text = "Country:",
                        getter = lambda p: p.get_str(),
                        field = "country",
                        required = True,
                        default_value = location.country
                    )

                if geographic_region is unset:
                    geographic_region = self._prompt_until_valid(
                        prompt_text = "Wider geographic region:",
                        getter = lambda p: p.get_str(),
                        field = "geographic_region",
                        default_value = location.geographic_region
                    )

                if decimal_latitude is unset:
                    decimal_latitude = self._prompt_until_valid(
                        prompt_text = "Latitude (decimal):",
                        getter = lambda p: p.get_float(),
                        field = "decimal_latitude",
                        default_value = location.decimal_latitude
                    )

                if decimal_longitude is unset:
                    decimal_longitude = self._prompt_until_valid(
                        prompt_text = "Longitude (decimal):",
                        getter = lambda p: p.get_float(),
                        field = "decimal_longitude",
                        default_value = location.decimal_longitude
                    )

                return Location(
                    location_id = location.location_id,
                    location_type = self._required(location_type, "location_type"),
                    iata_airport_code = self._optional(iata_airport_code),
                    icao_location_code = self._optional(icao_location_code),
                    location_name = self._required(location_name, "location_name"),
                    town_or_city = self._optional(town_or_city),
                    state_or_county = self._optional(state_or_county),
                    country = self._required(country, "country"),
                    geographic_region = self._optional(geographic_region),
                    decimal_latitude = self._optional(decimal_latitude),
                    decimal_longitude = self._optional(decimal_longitude)
                )

            except FieldValidationError as e:
                # Field validation error, so prompt for a field retry
                print(self._retry_message(e))

                if e.field == "location_type":
                    location_type = unset
                elif e.field == "location_name":
                    location_name = unset
                elif e.field == "iata_airport_code":
                    iata_airport_code = unset
                elif e.field == "icao_location_code":
                    icao_location_code = unset
                elif e.field == "town_or_city":
                    town_or_city = unset
                elif e.field == "state_or_county":
                    state_or_county = unset
                elif e.field == "country":
                    country = unset
                elif e.field == "geographic_region":
                    geographic_region = unset
                elif e.field == "decimal_latitude":
                    decimal_latitude = unset
                elif e.field == "decimal_longitude":
                    decimal_longitude = unset
            
            except DomainValidationError as e:
                # Cross-field validation error, so restart the process                
                print(self._retry_message(e))

                location_type = unset
                location_name = unset
                iata_airport_code = unset
                icao_location_code = unset
                town_or_city = unset
                state_or_county = unset
                country = unset
                geographic_region = unset
                decimal_latitude = unset
                decimal_longitude = unset

    def _prompt_delete_location(self) -> Location:

        # Prompt for the pilot to delete
        location = self._get_location_from_selection()
        print()

        # Delete will be cancelled if the user doesn't confirm
        self._prompt_delete_confirmation()
        
        return location

    def _get_location_from_selection(self) -> Location:

        location_id = None

        while location_id is None:
            location_id = self._prompt_until_valid(
                prompt_text = "Select a destination:",
                getter = lambda p: p.get_int(),
                field = "location_id",
                required = True,
                is_picklist = True,
                options = self._location_service.get_location_choices()
            )

        location = self._location_service.get_location_by_id(location_id)

        if location is None:
            raise ValueError("No location returned from selection.")
        if location.location_id is None:
            raise ValueError("No location returned from selection.")

        return location