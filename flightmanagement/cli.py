from pathlib import Path
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from flightmanagement.ui.main_menu import MainMenu
from flightmanagement.db.db import get_connection, initialise_schema, seed_database_data

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

        # Check if the database file already exists in the relevant location
        db_exists = DB_PATH.exists()

        # Initialise the database connection
        with get_connection(DB_PATH) as conn:

            # Initialise the database if the database file didn't exist on application start
            if not db_exists:
                initialise_database(conn)

            # Load the main menu
            MainMenu(session, bindings, conn).load()

    except Exception as e:
        print("Unexpected error:", e)
        raise

def initialise_database(conn):
    print("Initialising database for first use.....")
    initialise_schema(conn)
    seed_database_data(conn)
    print("Done!")

def print_welcome():
    print(r"""
    Welcome... to
    _____  _  _         _      _  
   |  ___|| ||_|       | |    | |    
   | |__  | | _  _____ | |___ | |_ 
   |  __| | || ||  _  ||  _  ||  _| 
   | |    | || || |_| || | | || |_ 
   |_|    |_||_||___  ||_| |_||___|
        ____  _   __| |  _          
       |  __|| | |____| | |  v0.1.0
       | |   | | _    _ | |___ 
       | |   | || |  | ||  _  |
       | |__ | || |__| || |_| |
       |____||_||______||_____|

   You know what the first rule is...
          """)

if __name__ == "__main__":
    main()