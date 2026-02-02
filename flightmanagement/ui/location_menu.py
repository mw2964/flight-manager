from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.location_service import LocationService
from flightmanagement.models.location import Location

class LocationMenu:

    __MENU_NAME = "Locations menu"
    __MENU_OPTIONS = [
        ("show", "Show all locations"),
        ("search", "Search locations"),
        ("add", "Add a location"),
        ("update", "Update a location"),
        ("delete", "Remove a location"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn=None, location_service=None):
        self.__location_service = location_service or LocationService(conn)
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
        print("\n>> Displaying all locations\n")
        print(self.__location_service.get_location_table())

    def __search_option(self) -> bool:
        print("\n>> Search for a location (or hit CTRL+C to cancel)\n")

        code = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter an airport code: ",
            allow_blank=True
        )        
        if code.is_cancelled:
            return False

        result = self.__location_service.search_locations("iata_airport_code", code.value)

        if len(result) == 0:
            print("\n     No matching results.")
        else:
            print(f"\n     {len(result)} match(es) found:\n")
            print(self.__location_service.get_results_view(result))

        return True

    def __add_option(self) -> bool:
        print("\n>> Add a location (or hit CTRL+C to cancel)\n")

        # Prompt the user to edit fields
        new = self.__prompt_add_location()
        if new is None: # Process was cancelled by the user
            return False

        try:
            self.__location_service.add_location(new)
            print("\nNew record successfully added.\n")
        except:
            print("\nError adding location.\n")
       
        return True

    def __update_option(self) -> bool:
        print("\n>> Update a location (or hit CTRL+C to cancel)\n")

        # Prompt for the location to edit
        location = self.__get_location_from_selection()
        if location is None or location.location_id is None:
            return False
        
        print(f"\nEditing information (location ID {id})\n")

        # Prompt the user to edit fields
        update = self.__prompt_update_location(location)
        if update is None: # Process was cancelled by the user
            return False

        # Update the aircraft record
        try:
            self.__location_service.update_location(location)
            print("\nRecord successfully updated.\n")
        except:
            print("\nError updating pilot.\n")

        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete a location (or hit CTRL+C to cancel)\n")

        # Prompt for the aircraft to delete
        location = self.__prompt_delete_location()
        if location is None:
            return False
        
        # Delete the location
        try:
            self.__location_service.delete_location(location)
            print("\nRecord successfully deleted.\n")
        except:
            print("\nError deleting aircraft.\n")
        
        return True

    def __prompt_add_location(self) -> Location | None:

        location_type = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select a location type:\n",
            options=[
                ("Airport", ("Airport")),
                ("Airfield", ("Airfield"))
            ],
            default_value="Airport",
            key_bindings=self.__bindings
        )
        if location_type.is_cancelled:
            return None
        print()

       
        iata_airport_code = None
        if location_type.value == "Airport":
            while True:
                iata_airport_code = UserPrompt(
                    session=self.__session,
                    prompt_type="text",
                    prompt="Enter the 3-character IATA airport code: ",
                    allow_blank=False
                )
                if iata_airport_code is None or Location.is_valid_iata_airport_code(iata_airport_code.value, location_type.value):
                    break
                else:
                    print("   Invalid airport code - please try again")
            if iata_airport_code.is_cancelled:
                return None
        

        icao_location_code = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the 4-character ICAO location code: ",
            allow_blank=location_type.value != "Airfield"
        )        
        if icao_location_code.is_cancelled:
            return None

        location_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the airport or airfield name: ",
            allow_blank=False
        )        
        if location_name.is_cancelled:
            return None

        town_or_city = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the city: ",            
            allow_blank=True
        )        
        if town_or_city.is_cancelled:
            return None

        state_or_county = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the state, county or province: ",            
            allow_blank=True
        )        
        if state_or_county.is_cancelled:
            return None

        country = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the country: ",
            allow_blank=True
        )        
        if country.is_cancelled:
            return None
        
        geographic_region = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the geographic region: ",
            allow_blank=True
        )        
        if geographic_region.is_cancelled:
            return None

        decimal_latitude = UserPrompt(
            session=self.__session,
            prompt_type="float",
            prompt="Enter the decimal latitude (between -90 and 90): ",
            allow_blank=True
        )        
        if decimal_latitude.is_cancelled:
            return None

        decimal_longitude = UserPrompt(
            session=self.__session,
            prompt_type="float",
            prompt="Enter the decimal longitude (between -180 and 180): ",
            allow_blank=True
        )        
        if decimal_longitude.is_cancelled:
            return None

        return Location(
            location_type=location_type.value,
            iata_airport_code=iata_airport_code.value if iata_airport_code else None,
            icao_location_code=icao_location_code.value,
            location_name=location_name.value,
            town_or_city=town_or_city.value,
            state_or_county=state_or_county.value,
            country=country.value,
            geographic_region=geographic_region.value,
            decimal_latitude=float(decimal_latitude.value) if decimal_latitude.value != '' else None,
            decimal_longitude=float(decimal_longitude.value) if decimal_latitude.value != '' else None
        )

    def __prompt_update_location(self, location: Location) -> Location | None:
        
        location_type = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Select a location type:\n",
            options=[
                ("Airport", ("Airport")),
                ("Airfield", ("Airfield"))
            ],
            default_value=location.location_type,
            key_bindings=self.__bindings
        )
        if location_type.is_cancelled:
            return None
        print()

        if location_type == "Airport":
            iata_airport_code = UserPrompt(
                session=self.__session,
                prompt_type="text",
                prompt="Enter the location code: ",
                allow_blank=False,
                default_value=location.iata_airport_code
            )        
            if iata_airport_code.is_cancelled:
                return None
        else:
            iata_airport_code = None
        
        icao_location_code = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the 4-character ICAO location code: ",
            allow_blank=location_type.value != "Airfield",
            default_value=location.icao_location_code
        )        
        if icao_location_code.is_cancelled:
            return None

        location_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the airport or airfield name: ",
            allow_blank=False,
            default_value=location.location_name
        )        
        if location_name.is_cancelled:
            return None

        town_or_city = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the city: ",            
            allow_blank=True,
            default_value=location.town_or_city
        )        
        if town_or_city.is_cancelled:
            return None

        state_or_county = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the state, county or province: ",            
            allow_blank=True,
            default_value=location.state_or_county
        )        
        if state_or_county.is_cancelled:
            return None

        country = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the country: ",
            allow_blank=True,
            default_value=location.country
        )        
        if country.is_cancelled:
            return None
        
        geographic_region = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter the geographic region: ",
            allow_blank=True,
            default_value=location.geographic_region
        )        
        if geographic_region.is_cancelled:
            return None
        print()

        decimal_latitude = UserPrompt(
            session=self.__session,
            prompt_type="float",
            prompt="Enter the decimal latitude (between -90 and 90 degrees): ",
            allow_blank=True,
            default_value=location.decimal_latitude
        )        
        if decimal_latitude.is_cancelled:
            return None
        print()

        decimal_longitude = UserPrompt(
            session=self.__session,
            prompt_type="float",
            prompt="Enter the decimal longitude (between -180 and 180 degrees): ",
            allow_blank=True,
            default_value=location.decimal_longitude
        )        
        if decimal_longitude.is_cancelled:
            return None
        print()

        return Location(
            location_id=location.location_id,
            location_type=location_type.value,
            iata_airport_code=iata_airport_code.value if iata_airport_code else None,
            icao_location_code=icao_location_code.value,
            location_name=location_name.value,
            town_or_city=town_or_city.value,
            state_or_county=state_or_county.value,
            country=country.value,
            geographic_region=geographic_region.value,
            decimal_latitude=float(decimal_latitude.value),
            decimal_longitude=float(decimal_longitude.value)
        )

    def __prompt_delete_location(self) -> Location | None:

        # Prompt for the location to delete
        location = self.__get_location_from_selection()
        if location is None or location.location_id is None:
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
        
        return location

    def __get_location_from_selection(self) -> Location | None:
        location_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Choose a location to update:\n",
            options=self.__location_service.get_location_choices(),
            key_bindings=self.__bindings
        )
        if location_id.is_cancelled:
            return None

        return self.__location_service.get_location_by_id(int(location_id.value))