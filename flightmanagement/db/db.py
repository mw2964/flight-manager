import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional
from flightmanagement.config import settings
    
def get_connection(db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)

    # Set the connection to return rows as dictionaries rather than lists
    conn.row_factory = sqlite3.Row

    # Foreign keys are off by default in SQLite, so need to set them to on
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn

@contextmanager
def transaction(conn):
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def initialise_schema(conn):

    # Drop the tables if they already exist
    conn.execute("DROP TABLE IF EXISTS flight")
    conn.execute("DROP TABLE IF EXISTS aircraft")
    conn.execute("DROP TABLE IF EXISTS pilot")
    conn.execute("DROP TABLE IF EXISTS airport")    

    # Create the tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS aircraft (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration VARCHAR(20) UNIQUE,
            manufacturer_serial_no INTEGER UNIQUE,
            icao_hex VARCHAR(20) UNIQUE,
            manufacturer VARCHAR(20),
            model VARCHAR(20),
            icao_type VARCHAR(20),
            status VARCHAR(20) CHECK(status IN ('Active', 'Inactive', 'Decommissioned'))
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS airport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(20) UNIQUE,
            name VARCHAR(20),
            city VARCHAR(20),
            country VARCHAR(20),
            region VARCHAR(20)
        )            
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS pilot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(20),
            family_name VARCHAR(20)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flight (
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
    """)

    # Create views
    conn.execute("""
        CREATE VIEW IF NOT EXISTS vw_denormalised_flights AS 
            SELECT 
                f.id AS flight_id,
                f.flight_number,
                ac.registration AS aircraft_registration,
                CONCAT(ac.manufacturer, ' ', ac.model) AS aircraft_type,
                apo.code AS origin,
                apd.code AS destination,
                IFNULL(f.departure_time_scheduled, '') AS departure_time_scheduled,
                IFNULL(f.arrival_time_scheduled, '') AS arrival_time_scheduled,
                IFNULL(f.departure_time_actual, '') AS departure_time_actual,
                IFNULL(f.arrival_time_actual, '') AS arrival_time_actual,
                CONCAT(p.first_name, ' ', p.family_name) AS pilot,
                CONCAT(cp.first_name, ' ', cp.family_name) AS copilot,
                f.status AS status
            FROM flight f
            LEFT JOIN aircraft ac ON ac.id = f.aircraft_id
            LEFT JOIN pilot p ON p.id = f.pilot_id
            LEFT JOIN pilot cp ON cp.id = f.copilot_id
            LEFT JOIN airport apo ON apo.id = f.origin_id
            LEFT JOIN airport apd ON apd.id = f.destination_id
    """)

    conn.commit()

def seed_database_data(conn):

    conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES
            ('G-EUUH', 1245, '406BCA', 'Airbus', 'A320-214', 'A320', 'Active'),
            ('EI-HAX', 62345, '4CA82F', 'Boeing', '737-8 MAX', 'B38M', 'Active'),
            ('G-VDOT', 312, '4078F2', 'Airbus', 'A350-941', 'A359', 'Active'),
            ('N24974', 36478, 'A2B3C4', 'Boeing', '787-9 Dreamliner', 'B789', 'Active'),
            ('YL-AAQ', 55089, '502D5F', 'Airbus', 'A220-300', 'BCS3', 'Active')
    """)

    conn.execute("""
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
    """)

    conn.execute("""
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
    """)

    conn.execute("""
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
    """)

    conn.commit()
