from flightmanagement.db.db import get_connection, initialise_schema, seed_database_data
from flightmanagement.db.db import transaction

class AdminService:

    def __init__(self, conn):
        self.conn = conn
    
    def initialise_database(self):
        with transaction(self.conn):
            initialise_schema(self.conn)
            seed_database_data(self.conn)