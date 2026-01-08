from flightmanagement.db.db import DBOperations

class AdminService:

    def __init__(self):
        self.__db = DBOperations()
    
    def initialise_database(self):
        self.__db.initialise_database()