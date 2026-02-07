from prompt_toolkit.shortcuts import choice
from flightmanagement.error import UserCancelled
from flightmanagement.ui.base_menu import BaseMenu
from flightmanagement.services.admin_service import AdminService

class AdminMenu(BaseMenu):

    def __init__(self, session, bindings, conn):
        super().__init__(session, bindings, conn)
        self.__admin_service = AdminService(conn)

        self._menu_name = "Main -> Admin"
        self._menu_options = [
            ("init_db", "Reinitialise database"),
            ("back", "Back to main menu")
    ]

    def load(self):
        while True:

            _selected_option = choice(message = self._format_title(self._menu_name), options = self._menu_options)

            try:
                if _selected_option == "init_db":
                    confirm = self._prompt_until_valid(
                        prompt_text = "\nWARNING - This will reset all data to the example data. Do you wish to continue? \n",
                        getter = lambda p: p.get_str(),
                        field = "confirm",
                        is_picklist = True,
                        required = True,
                        options = [
                            ("no", "No"),
                            ("yes", "Yes")
                        ],
                        default_value = "no"
                    )

                    if confirm == "yes":
                        self.__admin_service.initialise_database()
                        print("\nDatabase reinitialised successfully.")
                    else:
                        print("\nAction cancelled.")
                    
                elif _selected_option == "back":
                    return
            except UserCancelled as e:
                print(e)
                continue