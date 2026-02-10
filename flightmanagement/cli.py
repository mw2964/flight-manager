from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from flightmanagement.ui.main_menu import MainMenu
from flightmanagement.db.db import get_connection, initialise_schema, seed_database_data

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_FOLDER = "data"
DB_NAME = "FlightManagement.db"

def main():
    """
    This function serves as the main entry point for the FlightClub application.
    
    It initialises the interactive CLI, including custom key bindings to handle user cancellation,
    displays the welcome screen, and initialises the database connection.
    If the database does not already exist, it is created and initialised.
    Finally, it loads the main menu to begin user interaction. 
    """

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
        db_path = PROJECT_ROOT / "data" / DB_NAME
        db_exists = db_path.exists()

        # Initialise the database connection
        with get_connection(db_path) as conn:

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