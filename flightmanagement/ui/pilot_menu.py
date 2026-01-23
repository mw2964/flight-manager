from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import format_title
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.models.pilot import Pilot

class PilotMenu:

    __MENU_NAME = "Pilot menu"
    __MENU_OPTIONS = [
        ("show", "Show all pilots"),
        ("search", "Search pilots"),
        ("add", "Add a pilot"),
        ("update", "Update a pilot"),
        ("delete", "Remove a pilot"),
        ("back", "Back to main menu")
    ]

    def __init__(self, session: PromptSession, bindings: KeyBindings, conn=None, pilot_service=None):
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
        print("\n>> Displaying all pilots\n")
        print(self.__pilot_service.get_pilot_table())

    def __search_option(self) -> bool:
        print("\n>> Search for a pilot (or hit CTRL+C to cancel)\n")

        family_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a family name: ",
            allow_blank=True
        )        
        if family_name.is_cancelled:
            return False

        result = self.__pilot_service.search_pilots("family_name", family_name.value)

        if len(result) == 0:
            print("\n     No matching results.")
        else:
            print(f"\n     {len(result)} match(es) found:\n")
            print(self.__pilot_service.get_results_view(result))

        return True

    def __add_option(self) -> bool:
        print("\n>> Add a pilot (or hit CTRL+C to cancel)\n")

        # Prompt the user to complete fields
        new = self.__prompt_add_pilot()
        if new is None: # Process was cancelled by the user
            return False
        
        try:
            self.__pilot_service.add_pilot(new)
            print("\nNew record successfully added.\n")
        except:
            print("\nError adding pilot.\n")
       
        return True

    def __update_option(self) -> bool:
        print("\n>> Update a pilot (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to edit
        pilot = self.__get_pilot_from_selection()
        if pilot is None or pilot.id is None:
            return False

        print(f"\nEditing information (pilot ID {pilot.id})\n")

        # Prompt the user to edit fields
        update = self.__prompt_update_pilot(pilot)
        if update is None: # Process was cancelled by the user
            return False
        
        try:
            self.__pilot_service.update_pilot(update)
            print("\nRecord successfully updated.\n")
        except:
            print("\nError updating pilot.\n")
            
        return True

    def __delete_option(self) -> bool:
        print("\n>> Delete a pilot (or hit CTRL+C to cancel)\n")

        # Prompt for the pilot to delete
        pilot = self.__prompt_delete_pilot()
        if pilot is None:
            return False
        
        # Delete the pilot
        try:
            self.__pilot_service.delete_pilot(pilot)
            print("\nRecord successfully deleted.\n")
        except:
            print("\nError deleting pilot.\n")
        
        return True

    def __prompt_add_pilot(self) -> Pilot | None:

        first_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a first name: ",
            allow_blank=False
        )        
        if first_name.is_cancelled:
            return None
        
        family_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a family name: ",
            allow_blank=False
        )        
        if family_name.is_cancelled:
            return None
        print()

        return Pilot(
            first_name=first_name.value,
            family_name=family_name.value
        )

    def __prompt_update_pilot(self, pilot: Pilot) -> Pilot | None:

        first_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a first name: ",
            allow_blank=False,
            default_value=pilot.first_name
        )        
        if first_name.is_cancelled:
            return None
        
        family_name = UserPrompt(
            session=self.__session,
            prompt_type="text",
            prompt="Enter a family name: ",
            allow_blank=False,
            default_value=pilot.family_name
        )        
        if family_name.is_cancelled:
            return None
        print()

        return Pilot(
            id=pilot.id,
            first_name=first_name.value,
            family_name=family_name.value
        )

    def __prompt_delete_pilot(self) -> Pilot | None:

        # Prompt for the pilot to delete
        pilot = self.__get_pilot_from_selection()
        if pilot is None or pilot.id is None:
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
        
        return pilot

    def __get_pilot_from_selection(self) -> Pilot | None:
        pilot_id = UserPrompt(
            session=self.__session,
            prompt_type="choice",
            prompt="Choose a pilot to update:\n",
            options=self.__pilot_service.get_pilot_choices(),
            key_bindings=self.__bindings
        )
        if pilot_id.is_cancelled:
            return None

        return self.__pilot_service.get_pilot_by_id(int(pilot_id.value))