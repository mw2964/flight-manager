import sqlite3
from pathlib import Path
from typing import Optional
from flightmanagement.config import settings
from flightmanagement.models.flight import Flight

class DBOperations:

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DB_PATH = PROJECT_ROOT / "data" / "FlightManagement.db"
    
    def __init__(self):
        try:
            self.conn = sqlite3.connect(self.DB_PATH)
        except Exception as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()

    def get_connection(self):
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cur = self.conn.cursor()

    def create_table(self, sql):
        try:
            self.get_connection()
            self.cur.execute(sql)
            self.conn.commit()
            print("Table created successfully")
        except Exception as e:
            print(e)
        finally:
            self.conn.close()
    
    def drop_table(self, table_name: str):
        try:
            self.get_connection()
            self.cur.execute(f"DROP TABLE {table_name}")
            self.conn.commit()
            print(f"Table `{table_name}` dropped successfully")
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def get_row_by_id(self, table_name: str, id: int):
        
        try:
            self.get_connection()

            sql = f"SELECT * FROM {table_name} WHERE id = ?"
            
            self.cur.execute(sql, (id,))
            result = result = self.cur.fetchone()
            
            return result
        
        except Exception as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()

    def insert_row(self, table_name: str, data: dict):
        try:
            self.get_connection()
            self.cur.execute("PRAGMA foreign_keys = ON;")

            # Generate a comma-separated strings of fields and placeholders, and use to build the sql statement
            fields = ", ".join(data.keys())
            placeholders = ", ".join(f":{key}" for key in data)
            sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

            # Execute the insert in the database
            self.cur.execute(sql, data)
            self.conn.commit()
            print("Inserted data successfully")

        except Exception as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()

    def select_all(self, table_name: str):
        try:
            self.get_connection()
            self.cur.execute(f"SELECT * FROM {table_name}")
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def select_flights_view(self):
        try:
            self.get_connection()
            sql = """
                SELECT 
                    f.id AS flight_id,
                    f.flight_number,
                    ac.registration AS aircraft_registration,
                    CONCAT(ac.manufacturer, ' ', ac.model) AS aircraft_type,
                    apo.code AS origin,
                    apd.code AS destination,
                    f.departure_time_scheduled,
                    f.arrival_time_scheduled,
                    CONCAT(p.first_name, ' ', p.family_name) AS pilot,
                    CONCAT(cp.first_name, ' ', cp.family_name) AS copilot,
                    f.status AS status
                FROM flight f
                LEFT JOIN aircraft ac ON ac.id = f.aircraft_id
                LEFT JOIN pilot p ON p.id = f.pilot_id
                LEFT JOIN pilot cp ON cp.id = f.copilot_id
                LEFT JOIN airport apo ON apo.id = f.origin_id
                LEFT JOIN airport apd ON apd.id = f.destination_id
            """

            self.cur.execute(sql)
            result = self.cur.fetchall()
            return result

        except Exception as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()

    def search_data(self, table_name: str, field: str, value) -> Optional[int]:
        try:
            self.get_connection()
            
            sql = f"SELECT * FROM {table_name} WHERE {field} = ?"

            self.cur.execute(sql, (value,))

            result = self.cur.fetchone()            
            if type(result) == type(tuple()) and len(result) > 0:
                return result[0]

        except Exception as e:            
            print(e)
        finally:
            self.conn.close()

    def update_row(self, table_name: str, record_id: int, data: dict):
        try:
            self.get_connection()
            self.cur.execute("PRAGMA foreign_keys = ON;")

            updates = []
            for key, value in data.items():
                updates.append(f"{key} = :{key}")
            
            sql = f"UPDATE {table_name} SET {", ".join(updates)} WHERE id = {record_id}"

            result = self.cur.execute(sql, data)
            self.conn.commit()

            if result.rowcount != 0:
                print(str(result.rowcount) + " row(s) affected.")
            else:
                print("Cannot find this record in the database")

        except Exception as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()

    def delete_row(self, table_name: str, id: int):
        try:
            self.get_connection()
            self.cur.execute("PRAGMA foreign_keys = ON;")

            sql = f"DELETE FROM {table_name} WHERE id = {id}"

            result = self.cur.execute(sql)
            self.conn.commit()

            if result.rowcount != 0:
                print(str(result.rowcount) + " row(s) affected.")
            else:
                print("Cannot find this record in the database")

        except Exception as e:
            if type(e) is sqlite3.IntegrityError:
                print("Delete unsuccessful: the record has related records in another table.")
            else:
                print(e)
        finally:
            if self.conn:
                self.conn.close()
    
    def initialise_database(self):

        sql_create_aircraft = """
            CREATE TABLE aircraft (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration VARCHAR(20) UNIQUE,
                manufacturer_serial_no INTEGER UNIQUE,
                icao_hex VARCHAR(20) UNIQUE,
                manufacturer VARCHAR(20),
                model VARCHAR(20),
                icao_type VARCHAR(20),
                status VARCHAR(20) CHECK(status IN ('Active', 'Retired'))
            )
        """

        sql_populate_aircraft = """
            INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
            VALUES
                ('G-EUUH', 1245, '406BCA', 'Airbus', 'A320-214', 'A320', 'Active'),
                ('EI-HAX', 62345, '4CA82F', 'Boeing', '737-8 MAX', 'B38M', 'Active'),
                ('G-VDOT', 312, '4078F2', 'Airbus', 'A350-941', 'A359', 'Active'),
                ('N24974', 36478, 'A2B3C4', 'Boeing', '787-9 Dreamliner', 'B789', 'Active'),
                ('YL-AAQ', 55089, '502D5F', 'Airbus', 'A220-300', 'BCS3', 'Active')
        """

        sql_create_airport = """
			CREATE TABLE airport (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				code VARCHAR(20) UNIQUE,
				name VARCHAR(20),
				city VARCHAR(20),
				country VARCHAR(20),
				region VARCHAR(20)
			)            
        """
        sql_populate_airport = """
            INSERT INTO airport(code, name, city, country, region)
            VALUES
                ('LHR', 'London Heathrow', 'London', 'United Kingdom', 'Europe'),
                ('AMS', 'Amsterdam Schiphol', 'Amsterdam', 'Netherlands', 'Europe'),
                ('CDG', 'Paris Charles de Gaulle', 'Paris', 'France', 'Europe'),
                ('FRA', 'Frankfurt', 'Frankfurt', 'Germany', 'Europe'),
                ('MAD', 'Madrid Barajas', 'Madrid', 'Spain', 'Europe'),
                ('DXB', 'Dubai International', 'Dubai', 'United Arab Emirates', 'Middle East'),
                ('DOH', 'Hamad International', 'Doha', 'Qatar', 'Middle East'),
                ('JFK', 'John F. Kennedy International', 'New York', 'United States', 'North America'),
                ('LAX', 'Los Angeles International', 'Los Angeles', 'United States', 'North America'),
                ('YYZ', 'Toronto Pearson', 'Toronto', 'Canada', 'North America'),
                ('DEL', 'Indira Gandhi International', 'New Delhi', 'India', 'South Asia'),
                ('SIN', 'Singapore Changi', 'Singapore', 'Singapore', 'Southeast Asia'),
                ('HKG', 'Hong Kong International', 'Hong Kong', 'China (SAR)', 'East Asia'),
                ('NRT', 'Tokyo Narita', 'Tokyo', 'Japan', 'East Asia'),
                ('SYD', 'Sydney Kingsford Smith', 'Sydney', 'Australia', 'Oceania')
        """

        sql_create_pilot = """
			CREATE TABLE pilot (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				first_name VARCHAR(20),
				family_name VARCHAR(20)
			)
        """

        sql_populate_pilot = """
            INSERT INTO pilot (first_name, family_name)
            VALUES
                ('Alex', 'Morrison'),
                ('Emily', 'Carter'),
                ('Daniel', 'Hughes'),
                ('Sophie', 'Bennett'),
                ('Michael', 'Reed'),
                ('Laura', 'Whitaker'),
                ('James', 'Thornton'),
                ('Priya', 'Malhotra'),
                ('Noah', 'Feldman'),
                ('Isabella', 'Russo')
        """

        sql_create_flight = """
			CREATE TABLE flight (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				flight_number VARCHAR(20),
				aircraft_id INTEGER,
				origin_id INTEGER,
				destination_id INTEGER,
				pilot_id INTEGER,
				copilot_id INTEGER,
				departure_time_scheduled TEXT,
				arrival_time_scheduled TEXT,
				departure_time_actual TEXT,
				arrival_time_actual TEXT,
				status VARCHAR(20) CHECK(status IN ('Scheduled', 'On time', 'Delayed', 'Boarding', 'Closed', 'Departed', 'Arrived')),
				FOREIGN KEY(aircraft_id) REFERENCES aircraft(id),
				FOREIGN KEY(origin_id) REFERENCES airport(id),
				FOREIGN KEY(destination_id) REFERENCES airport(id),
				FOREIGN KEY(pilot_id) REFERENCES pilot(id),
				FOREIGN KEY(copilot_id) REFERENCES pilot(id)
			)
        """

        sql_populate_flight = """
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES
                ('ZMY1423', 1, 1, 2, 1, 10, '2026-01-09 15:30', '2026-01-09 16:55', '2026-01-09 15:30', '2026-01-09 16:50', 'Arrived'),
                ('ZMY65', 2, 1, 3, 2, 3, '2026-01-14 09:50', '2026-01-14 11:15', '2026-01-14 09:50', '2026-01-14 11:15', 'Arrived'),
                ('ZMY324', 3, 1, 4, 3, 6, '2026-02-03 18:20', '2026-02-03 20:05', '2026-02-03 18:35', '2026-02-03 20:15', 'Arrived'),
                ('ZMY147', 4, 1, 5, 4, 3, '2026-03-19 06:50', '2026-03-19 09:20', '2026-03-19 06:50', '2026-03-19 09:35', 'Arrived'),
                ('ZMY1545', 5, 1, 6, 5, 7, '2026-04-07 21:00', '2026-04-08 04:05', '2026-04-07 21:00', NULL, 'Departed'),
                ('ZMY1245', 1, 1, 7, 6, 2, '2026-05-25 13:40', '2026-05-25 20:50', '2026-05-25 13:40', NULL, 'Departed'),
                ('ZMY6654', 2, 8, 1, 7, 9, '2026-06-11 00:15', '2026-06-11 07:30', NULL, NULL, 'Closed'),
                ('ZMY3418', 3, 9, 1, 8, 3, '2026-07-29 17:50', '2026-07-30 04:25', NULL, NULL, 'Boarding'),
                ('ZMY3654', 4, 10, 1, 9, 8, '2026-08-08 10:10', '2026-08-08 17:35', NULL, NULL, 'Delayed'),
                ('ZMY2697', 5, 11, 1, 10, 2, '2026-09-14 23:40', '2026-09-15 08:55', NULL, NULL, 'On time'),
                ('ZMY144', 1, 12, 1, 1, 4, '2026-10-02 04:30', '2026-10-02 18:00', NULL, NULL, 'On time'),
                ('ZMY1423', 2, 1, 2, 4, 8, '2026-11-18 15:20', '2026-11-18 16:45', NULL, NULL, 'Scheduled')
        """

        try:
            
            # Drop existing tables
            for table in ['Flight', 'Pilot', 'Aircraft', 'Airport']:
                self.drop_table(table)

            # Create the tables
            self.create_table(sql_create_aircraft)
            self.create_table(sql_create_airport)
            self.create_table(sql_create_pilot)
            self.create_table(sql_create_flight)
            
            # Populate the tables with example data
            self.get_connection()
            self.cur.execute(sql_populate_aircraft)
            self.cur.execute(sql_populate_airport)
            self.cur.execute(sql_populate_pilot)
            self.cur.execute(sql_populate_flight)
            self.conn.commit()
            print("Database initialised successfully")
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

        
