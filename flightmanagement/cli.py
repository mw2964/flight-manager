from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from flightmanagement.ui.main_menu import MainMenu
from flightmanagement.db.db import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "FlightManagement.db"

def main():

    try:
        # Initialise UI prompt session
        bindings = KeyBindings()

        @bindings.add('c-c')
        def _(event):
            event.app.exit(result="__CANCEL__")

        session = PromptSession(key_bindings=bindings)

        # Print the welcome screen
        print("""
***********
FLIGHT CLUB
V0.1.0
***********""")
    
        # Initialise the database connection
        conn = get_connection(DB_PATH)

        MainMenu(session, bindings, conn).load()
    except RuntimeError as e:
        print(e)

if __name__ == "__main__":
    main()