from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from flightmanagement.ui.main_menu import MainMenu
from flightmanagement.db.db import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "FlightManagement.db"

def main():

    try:
        # Initialise the UI prompt session and key bindings to capture cancel actions
        bindings = KeyBindings()

        @bindings.add('c-c')
        def _(event):
            event.app.exit(result="__CANCEL__")

        session = PromptSession(key_bindings=bindings)

        # Print the welcome screen
        print_welcome()
    
        # Initialise the database connection
        conn = get_connection(DB_PATH)

        # Load the main menu
        MainMenu(session, bindings, conn).load()

    except RuntimeError as e:
        print(e)

def print_welcome():
    print(r"""
    ______ _ _       _     _       ____  _       _     
   |  ____| (_)     | |   | |     / ___|| |     | |    
   | |__  | |_  __ _| |__ | |_   | |    | |_   _| |__  
   |  __| | | |/ _` | '_ \| __|  | |    | | | | | '_ \ 
   | |    | | | (_| | | | | |_   | |___ | | |_| | |_) |
   |_|    |_|_|\__, |_| |_|\__|   \____||_|\__,_|_.__/ 
                __/ |     ✈️                   v0.1.0
               |___/                                          
   
   The first rule is...
          """)

if __name__ == "__main__":
    main()