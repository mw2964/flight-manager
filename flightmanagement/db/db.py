import sqlite3
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def get_connection(db_path: Path):
    conn = sqlite3.connect(db_path, timeout=10)

    # Set the connection to return table rows as dictionaries rather than lists
    conn.row_factory = sqlite3.Row

    # Foreign keys are off by default in SQLite, so set them to on to enforce referential integrity
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def transaction(conn):
    try:        
        yield
        conn.commit()
    except sqlite3.DatabaseError:
        conn.rollback()
        raise

def initialise_schema(conn):

    with transaction(conn):

        # Create the tables and indices
        conn.execute("""
            CREATE TABLE IF NOT EXISTS aircraft_types (
                aircraft_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                icao_type TEXT,
                UNIQUE(manufacturer, model)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS aircraft (
                aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
                aircraft_type_id INTEGER NOT NULL REFERENCES aircraft_types(aircraft_type_id) ON DELETE RESTRICT,
                registration TEXT NOT NULL UNIQUE,
                manufacturer_serial_no INTEGER UNIQUE,
                icao_hex TEXT UNIQUE,
                aircraft_status TEXT NOT NULL CHECK(aircraft_status IN ('Active', 'Inactive', 'Decommissioned'))
            )          
        """)
        conn.execute('CREATE INDEX idx_aircraft_aircraft_type_id ON aircraft(aircraft_type_id)')

        conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_type TEXT NOT NULL CHECK(location_type IN ('Airport', 'Airfield')),
                icao_location_code TEXT UNIQUE CHECK(location_type = 'Airport' OR icao_location_code IS NOT NULL),
                iata_airport_code TEXT UNIQUE CHECK(location_type <> 'Airport' OR iata_airport_code IS NOT NULL),
                location_name TEXT NOT NULL,
                town_or_city TEXT CHECK(location_type <> 'Airport' OR town_or_city IS NOT NULL),
                state_or_county TEXT,
                country TEXT NOT NULL,
                geographic_region TEXT,
                decimal_latitude REAL,
                decimal_longitude REAL
            )
        """)
        conn.execute('CREATE INDEX idx_locations_location_type ON locations(location_type)')

        conn.execute("""
            CREATE TABLE IF NOT EXISTS terminals (
                terminal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL REFERENCES locations(location_id) ON DELETE RESTRICT,
                terminal_name TEXT NOT NULL,
                UNIQUE(location_id, terminal_name)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS gates (
                gate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                terminal_id INTEGER NOT NULL REFERENCES terminals(terminal_id) ON DELETE RESTRICT,
                gate_number TEXT NOT NULL,
                UNIQUE(terminal_id, gate_number)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS staff_members (
                staff_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_number TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                family_name TEXT NOT NULL,
                employment_status TEXT NOT NULL CHECK(employment_status IN ('Current', 'Left')),
                employment_start_date DATE NOT NULL CHECK(employment_start_date IS date(employment_start_date)),
                employment_end_date DATE CHECK(employment_end_date IS date(employment_end_date) AND (employment_status <> 'Left' OR employment_end_date IS NOT NULL))
            )
        """)
        conn.execute('CREATE INDEX idx_staff_name ON staff_members(first_name, family_name)')

        conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_bookings (
                staff_member_id INTEGER NOT NULL REFERENCES staff_members(staff_member_id) ON DELETE CASCADE,
                leave_date DATE NOT NULL CHECK(leave_date IS date(leave_date)),
                leave_type TEXT CHECK(leave_type IN ('Annual leave', 'Sick leave', 'Parental leave', 'Compassionate leave', 'Study leave')),
                PRIMARY KEY (staff_member_id, leave_date)
            )
        """)
        conn.execute('CREATE INDEX idx_leave_bookings_leave_date ON leave_bookings(leave_date)')

        conn.execute("""
            CREATE TABLE IF NOT EXISTS pilots (
                staff_member_id INTEGER NOT NULL PRIMARY KEY REFERENCES staff_members(staff_member_id) ON DELETE RESTRICT,
                license_number TEXT UNIQUE,
                license_type TEXT,
                license_expiration_date DATE CHECK(license_expiration_date = date(license_expiration_date))
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS flight_time_logs (
                staff_member_id INTEGER NOT NULL REFERENCES pilots(staff_member_id) ON DELETE CASCADE,
                effective_date DATE NOT NULL CHECK(effective_date IS date(effective_date)),
                flight_hours REAL NOT NULL CHECK(flight_hours <= 24),
                PRIMARY KEY (staff_member_id, effective_date)
            )
        """)
        conn.execute('CREATE INDEX idx_flight_time_logs_effective_date ON flight_time_logs(effective_date)')

        conn.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                flight_id INTEGER PRIMARY KEY AUTOINCREMENT,	
                aircraft_id INTEGER REFERENCES aircraft(aircraft_id) ON DELETE RESTRICT,
                origin_location_id INTEGER NOT NULL REFERENCES locations(location_id) ON DELETE RESTRICT,
                destination_location_id INTEGER NOT NULL REFERENCES locations(location_id) ON DELETE RESTRICT,
                departure_gate_id INTEGER REFERENCES gates(gate_id) ON DELETE SET NULL,
                arrival_gate_id INTEGER REFERENCES gates(gate_id) ON DELETE SET NULL,
                captain_id INTEGER REFERENCES pilots(staff_member_id) ON DELETE RESTRICT,
                first_officer_id INTEGER REFERENCES pilots(staff_member_id) ON DELETE RESTRICT,
                flight_number TEXT NOT NULL,
                scheduled_departure_date DATE NOT NULL CHECK(scheduled_departure_date = date(scheduled_departure_date)),
                scheduled_departure_time TIME NOT NULL CHECK(scheduled_departure_time GLOB '[0-1][0-9]:[0-5][0-9]' OR scheduled_departure_time GLOB '2[0-3]:[0-5][0-9]'),
                scheduled_arrival_date DATE NOT NULL CHECK(scheduled_arrival_date = date(scheduled_arrival_date)),
                scheduled_arrival_time TIME NOT NULL CHECK(scheduled_arrival_time GLOB '[0-1][0-9]:[0-5][0-9]' OR scheduled_arrival_time GLOB '2[0-3]:[0-5][0-9]'),
                confirmed_departure_date DATE CHECK(confirmed_departure_date = date(confirmed_departure_date)),
                confirmed_departure_time TIME CHECK(confirmed_departure_time GLOB '[0-1][0-9]:[0-5][0-9]' OR confirmed_departure_time GLOB '2[0-3]:[0-5][0-9]'),
                confirmed_arrival_date DATE CHECK(confirmed_arrival_date = date(confirmed_arrival_date)),
                confirmed_arrival_time TIME CHECK(confirmed_arrival_time GLOB '[0-1][0-9]:[0-5][0-9]' OR confirmed_arrival_time GLOB '2[0-3]:[0-5][0-9]'),
                flight_status TEXT NOT NULL DEFAULT 'Scheduled' CHECK(flight_status IN ('Scheduled', 'On time', 'Delayed', 'Boarding', 'Closed', 'Departed', 'Arrived')),
                UNIQUE(flight_number, scheduled_departure_date)
            )
        """)
        conn.execute('CREATE INDEX idx_flights_aircraft_id ON flights(aircraft_id)')
        conn.execute('CREATE INDEX idx_flights_origin_location_id ON flights(origin_location_id)')
        conn.execute('CREATE INDEX idx_flights_destination_location_id ON flights(destination_location_id)')
        conn.execute('CREATE INDEX idx_flights_departure_gate_id ON flights(departure_gate_id)')
        conn.execute('CREATE INDEX idx_flights_arrival_gate_id ON flights(arrival_gate_id)')
        conn.execute('CREATE INDEX idx_flights_captain_id ON flights(captain_id)')
        conn.execute('CREATE INDEX idx_flights_first_officer_id ON flights(first_officer_id)')
        conn.execute('CREATE INDEX idx_flights_flight_number ON flights(flight_number)')
        conn.execute('CREATE INDEX idx_flights_flight_status ON flights(flight_status)')
        conn.execute('CREATE INDEX idx_flights_scheduled_departure ON flights(scheduled_departure_date, scheduled_departure_time)')
        conn.execute('CREATE INDEX idx_flights_scheduled_arrival ON flights(scheduled_arrival_date, scheduled_arrival_time)')
        conn.execute('CREATE INDEX idx_flights_confirmed_departure ON flights(confirmed_departure_date, confirmed_departure_time)')
        conn.execute('CREATE INDEX idx_flights_confirmed_arrival ON flights(confirmed_arrival_date, confirmed_arrival_time)')

        conn.execute("""
            CREATE TABLE IF NOT EXISTS flight_relief_pilots (
                flight_id INTEGER NOT NULL REFERENCES flights(flight_id) ON DELETE CASCADE,
                staff_member_id INTEGER NOT NULL REFERENCES pilots(staff_member_id) ON DELETE CASCADE,
                PRIMARY KEY (flight_id, staff_member_id)
            )
        """)
        conn.execute('CREATE INDEX idx_flight_relief_pilots_staff_member_id ON flight_relief_pilots(staff_member_id)')


        # Create views

        conn.execute("""
            CREATE VIEW IF NOT EXISTS vw_staff_pilots AS
                SELECT *
                FROM staff_members
                NATURAL JOIN pilots;
        """)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS vw_aircraft AS
                SELECT *
                FROM aircraft
                NATURAL JOIN aircraft_types;
        """)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS vw_flight_summary AS
            SELECT
                f.flight_id,
                f.flight_number,
                ifnull(a.registration, '') as aircraft_registration,
                trim(ifnull(coalesce(a.manufacturer, '') || ' ' || coalesce(a.model, ''), '')) AS aircraft_type,
                ifnull(coalesce(o.iata_airport_code, o.icao_location_code), '') as origin_location,
                ifnull(o.town_or_city, '') AS origin_town_or_city,
                ifnull(dt.terminal_name, '') as departure_terminal,
                ifnull(dg.gate_number, '') as departure_gate,    
                ifnull(d.iata_airport_code, d.icao_location_code) as destination_location,
                ifnull(d.town_or_city, '') AS destination_town_or_city,
                ifnull(at.terminal_name, '') as arrival_terminal,
                ifnull(ag.gate_number, '') as arrival_gate,
                ifnull(cp.first_name || ' ' || cp.family_name, '') AS captain_name,
                ifnull(fo.first_name || ' ' || fo.family_name, '') AS first_officer_name,
                ifnull(rp.relief_pilots, '') AS relief_pilots,
                f.scheduled_departure_date,
                f.scheduled_departure_time,
                f.scheduled_arrival_date,
                f.scheduled_arrival_time,
                f.confirmed_departure_date,
                f.confirmed_departure_time,
                f.confirmed_arrival_date,
                f.confirmed_arrival_time,
                f.flight_status
            FROM flights f
            LEFT JOIN vw_aircraft a ON a.aircraft_id = f.aircraft_id
            LEFT JOIN locations o ON o.location_id = f.origin_location_id
            LEFT JOIN gates dg ON dg.gate_id = f.departure_gate_id
            LEFT JOIN terminals dt ON dt.terminal_id = dg.terminal_id
            LEFT JOIN gates ag ON ag.gate_id = f.arrival_gate_id
            LEFT JOIN terminals at ON at.terminal_id = ag.terminal_id
            LEFT JOIN locations d ON d.location_id = f.destination_location_id
            LEFT JOIN vw_staff_pilots cp ON cp.staff_member_id = f.captain_id
            LEFT JOIN vw_staff_pilots fo ON fo.staff_member_id = f.first_officer_id
            LEFT JOIN (
                SELECT
                    frp.flight_id,
                    group_concat(vsp.first_name || ' ' || vsp.family_name, ', ') AS relief_pilots
                FROM flight_relief_pilots frp
                JOIN vw_staff_pilots vsp ON vsp.staff_member_id = frp.staff_member_id
                GROUP BY frp.flight_id
            ) rp ON rp.flight_id = f.flight_id
        """)

    #conn.commit()

def seed_database_data(conn):

    with transaction(conn):

        conn.execute("""
            INSERT INTO aircraft_types (manufacturer, model, icao_type)
            VALUES 
                ('Airbus', 'A320', 'A320'),
                ('Airbus', 'A321', 'A321'),
                ('Airbus', 'A319', 'A319'),
                ('Boeing', '737-800', 'B738'),
                ('Boeing', '737 MAX 8', 'B38M'),
                ('Boeing', '777-300ER', 'B77W'),
                ('Boeing', '787-9', 'B789'),
                ('Airbus', 'A350-900', 'A359'),
                ('Embraer', 'E190', 'E190'),
                ('ATR', '72-600', 'AT76')
        """)

        conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (1, 'G-EUUH', 1561245, '406BCA', 'Active'),
                (8, 'EI-HAX', 62345, '4CA82F', 'Active'),
                (6, 'G-VDOT', 45312, '4078F2', 'Active'),
                (1, 'G-LKSD', 36478, 'A2B3C4', 'Active'),
                (6, 'YL-AAQ', 55089, '502D5F', 'Active'),
                (7, 'G-PPWO', 126445, 'A1B2C3', 'Inactive'),
                (7, 'G-YYAA', 1156592, '4CA123', 'Inactive'),
                (7, 'L-LKED', 144554, '7809AB', 'Decommissioned'),
                (9, 'G-QTYW', 561557, '3C4D5E', 'Active'),
                (7, 'G-PDOT', 551547, 'E01234', 'Active')
        """)

        conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619),
                ('Airport', 'EGKK', 'LGW', 'London Gatwick Airport', 'London', 'West Sussex', 'United Kingdom', 'Europe', 51.1537, -0.1821),
                ('Airport', 'EGCC', 'MAN', 'Manchester Airport', 'Manchester', 'Greater Manchester', 'United Kingdom', 'Europe', 53.3537, -2.2749),
                ('Airport', 'EGPH', 'EDI', 'Edinburgh Airport', 'Edinburgh', 'Scotland', 'United Kingdom', 'Europe', 55.95, -3.3725),
                ('Airport', 'EGBB', 'BHX', 'Birmingham Airport', 'Birmingham', 'West Midlands', 'United Kingdom', 'Europe', 52.4539, -1.748),
                ('Airport', 'EIDW', 'DUB', 'Dublin Airport', 'Dublin', 'County Dublin', 'Ireland', 'Europe', 53.4213, -6.2701),
                ('Airport', 'LFPG', 'CDG', 'Paris Charles de Gaulle Airport', 'Paris', 'Île-de-France', 'France', 'Europe', 49.0097, 2.5479),
                ('Airport', 'EDDF', 'FRA', 'Frankfurt Airport', 'Frankfurt', 'Hesse', 'Germany', 'Europe', 50.0379, 8.5622),
                ('Airport', 'EHAM', 'AMS', 'Amsterdam Schiphol Airport', 'Amsterdam', 'North Holland', 'Netherlands', 'Europe', 52.3105, 4.7683),
                ('Airport', 'LEMD', 'MAD', 'Adolfo Suárez Madrid–Barajas Airport', 'Madrid', 'Community of Madrid', 'Spain', 'Europe', 40.4722, -3.5609),
                ('Airport', 'KJFK', 'JFK', 'John F. Kennedy International Airport', 'New York', 'New York', 'United States', 'North America', 40.6413, -73.7781),
                ('Airport', 'KLAX', 'LAX', 'Los Angeles International Airport', 'Los Angeles', 'California', 'United States', 'North America', 33.9416, -118.4085),
                ('Airport', 'OMDB', 'DXB', 'Dubai International Airport', 'Dubai', 'Dubai', 'United Arab Emirates', 'Middle East', 25.2532, 55.3657),
                ('Airport', 'WSSS', 'SIN', 'Singapore Changi Airport', 'Singapore', NULL, 'Singapore', 'Southeast Asia', 1.3644, 103.9915),
                ('Airport', 'YSSY', 'SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'New South Wales', 'Australia', 'Oceania', -33.9399, 151.1753),
                ('Airfield', 'EGSU', NULL, 'Duxford Aerodrome', 'Duxford', 'Cambridgeshire', 'United Kingdom', 'Europe', 52.0908, 0.1319),
                ('Airfield', 'EGLM', NULL, 'White Waltham Airfield', 'Maidenhead', 'Berkshire', 'United Kingdom', 'Europe', 51.5008, -0.7719),
                ('Airfield', 'EGHA', NULL, 'Compton Abbas Airfield', 'Shaftesbury', 'Dorset', 'United Kingdom', 'Europe', 50.9672, -2.1533)
        """)

        conn.execute("""
            INSERT INTO terminals (location_id, terminal_name)
            VALUES
                (1, 'Terminal 2'),
                (1, 'Terminal 3'),
                (1, 'Terminal 4'),
                (1, 'Terminal 5'),
                (2, 'North Terminal'),
                (2, 'South Terminal'),
                (3, 'Terminal 1'),
                (3, 'Terminal 2'),
                (3, 'Terminal 3'),
                (4, 'Terminal 1'),
                (5, 'Terminal 1'),
                (6, 'Terminal 1'),
                (6, 'Terminal 2'),
                (7, 'Terminal 1'),
                (7, 'Terminal 2A'),
                (7, 'Terminal 2B'),
                (7, 'Terminal 2C'),
                (7, 'Terminal 2D'),
                (7, 'Terminal 2E'),
                (7, 'Terminal 2F'),
                (7, 'Terminal 2G'),
                (7, 'Terminal 3'),
                (8, 'Terminal 1'),
                (9, 'Terminal 1'),
                (10, 'Terminal 1'),
                (10, 'Terminal 2'),
                (10, 'Terminal 3'),
                (10, 'Terminal 4'),
                (10, 'Terminal 4 Satellite'),
                (11, 'Terminal 1'),
                (11, 'Terminal 4'),
                (11, 'Terminal 5'),
                (11, 'Terminal 7'),
                (11, 'Terminal 8'),
                (12, 'Terminal 1'),
                (12, 'Terminal 2'),
                (12, 'Terminal 3'),
                (12, 'Terminal 4'),
                (12, 'Terminal 5'),
                (12, 'Terminal 6'),
                (12, 'Terminal 7'),
                (12, 'Terminal 8'),
                (12, 'Tom Bradley International Terminal (TBIT)'),
                (13, 'Terminal 1'),
                (13, 'Terminal 2'),
                (13, 'Terminal 3'),
                (14, 'Terminal 1'),
                (14, 'Terminal 2'),
                (14, 'Terminal 3'),
                (14, 'Terminal 4'),
                (15, 'Terminal 1 International'),
                (15, 'Terminal 2 Domestic'),
                (15, 'Terminal 3 Domestic')
        """)

        conn.execute("""
            INSERT INTO gates (terminal_id, gate_number)
            VALUES
                (1, '1'),
                (1, '2'),
                (1, '3'),
                (1, '4'),
                (2, '1'),
                (2, '2'),
                (2, '3'),
                (2, '4'),
                (2, '5'),
                (3, '1'),
                (3, '2'),
                (3, '3'),
                (4, 'A1'),
                (4, 'A2'),
                (4, 'A3'),
                (4, 'A4'),
                (4, 'A5'),
                (5, '1'),
                (5, '2'),
                (5, '3'),
                (5, '4'),
                (5, '5'),
                (6, '1'),
                (6, '2'),
                (6, '3'),
                (6, '4'),
                (6, '5'),
                (6, '6'),
                (6, '7'),
                (7, '1'),
                (7, '2'),
                (7, '3'),
                (7, '4'),
                (7, '5'),
                (8, 'A1'),
                (8, 'A2'),
                (8, 'A3'),
                (8, 'A4'),
                (9, '1'),
                (9, '2'),
                (9, '3'),
                (9, '4'),
                (9, '5'),
                (10, '1'),
                (10, '2'),
                (10, '3'),
                (10, '4'),
                (10, '5'),
                (11, '1'),
                (11, '2'),
                (11, '3'),
                (11, '4'),
                (11, '5'),
                (12, 'A1'),
                (12, 'A2'),
                (12, 'A3'),
                (12, 'A4'),
                (12, 'A5'),
                (12, 'A6'),
                (13, '1'),
                (13, '2'),
                (13, '3'),
                (13, '4'),
                (13, '5'),
                (13, '6'),
                (14, '1'),
                (14, '2'),
                (14, '3'),
                (14, '4'),
                (14, '5'),
                (14, '6'),
                (15, '1'),
                (15, '2'),
                (15, '3'),
                (15, '4'),
                (15, '5'),
                (16, 'A1'),
                (16, 'A2'),
                (16, 'A3'),
                (16, 'A4'),
                (16, 'A5'),
                (17, '1'),
                (17, '2'),
                (17, '3'),
                (17, '4'),
                (17, '5'),
                (18, '1'),
                (18, '2'),
                (18, '3'),
                (18, '4'),
                (18, '5'),
                (19, '1'),
                (19, '2'),
                (19, '3'),
                (19, '4'),
                (19, '5'),
                (20, 'A1'),
                (20, 'A2'),
                (20, 'A3'),
                (20, 'A4'),
                (20, 'A5'),
                (21, '1'),
                (21, '2'),
                (21, '3'),
                (21, '4'),
                (22, '1'),
                (22, '2'),
                (22, '3'),
                (22, '4'),
                (23, '1'),
                (23, '2'),
                (23, '3'),
                (23, '4'),
                (24, 'A1'),
                (24, 'A2'),
                (24, 'A3'),
                (24, 'A4'),
                (25, '1'),
                (25, '2'),
                (25, '3'),
                (25, '4'),
                (25, '5'),
                (26, '1'),
                (26, '2'),
                (26, '3'),
                (26, '4'),
                (27, '1'),
                (27, '2'),
                (27, '3'),
                (27, '4'),
                (28, 'A1'),
                (28, 'A2'),
                (28, 'A3'),
                (28, 'A4'),
                (29, '1'),
                (29, '2'),
                (29, '3'),
                (29, '4'),
                (30, '1'),
                (30, '2'),
                (30, '3'),
                (31, '1'),
                (31, '2'),
                (31, '3'),
                (31, '4'),
                (32, 'A1'),
                (32, 'A2'),
                (32, 'A3'),
                (32, 'A4'),
                (33, '1'),
                (33, '2'),
                (33, '3'),
                (34, '1'),
                (34, '2'),
                (34, '3'),
                (34, '4'),
                (35, '1'),
                (35, '2'),
                (35, '3'),
                (35, '4'),
                (35, '5'),
                (36, 'A1'),
                (36, 'A2'),
                (36, 'A3'),
                (36, 'A4'),
                (37, '1'),
                (37, '2'),
                (37, '3'),
                (38, '1'),
                (38, '2'),
                (39, '1'),
                (39, '2'),
                (39, '3'),
                (39, '4'),
                (40, 'A1'),
                (40, 'A2'),
                (40, 'A3'),
                (41, '1'),
                (41, '2'),
                (41, '3'),
                (41, '4'),
                (41, '5'),
                (42, '1'),
                (42, '2'),
                (42, '3'),
                (42, '4'),
                (43, '1'),
                (43, '2'),
                (43, '3'),
                (43, '4'),
                (43, '5'),
                (44, 'A1'),
                (44, 'A2'),
                (44, 'A3'),
                (45, '1'),
                (45, '2'),
                (45, '3'),
                (46, '1'),
                (46, '2'),
                (46, '3'),
                (47, '1'),
                (47, '2'),
                (47, '3'),
                (47, '4'),
                (48, 'A1'),
                (48, 'A2'),
                (48, 'A3'),
                (48, 'A4'),
                (48, 'A5'),
                (48, 'A6'),
                (49, '1'),
                (49, '2'),
                (49, '3'),
                (49, '4'),
                (50, '1'),
                (50, '2'),
                (50, '3'),
                (50, '4'),
                (51, '1'),
                (51, '2'),
                (51, '3'),
                (51, '4'),
                (52, 'A1'),
                (52, 'A2'),
                (52, 'A3'),
                (52, 'A4'),
                (52, 'A5'),
                (53, '1'),
                (53, '2'),
                (53, '3'),
                (53, '4'),
                (53, '5')
        """)

        conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Morrison', 'Current', '2014-04-13', NULL),
                ('FC002', 'Emily', 'Carter', 'Current', '2021-10-23', NULL),
                ('FC003', 'Xian', 'Liu', 'Current', '2022-12-27', NULL),
                ('FC004', 'Sophie', 'Bennett', 'Current', '2016-02-18', NULL),
                ('FC005', 'Michael', 'Reed', 'Left', '2023-01-26', '2025-01-18'),
                ('FC006', 'Laura', 'Whitaker', 'Current', '2012-07-10', NULL),
                ('FC007', 'James', 'Thornton', 'Left', '2014-03-21', '2018-04-26'),
                ('FC008', 'Priya', 'Malhotra', 'Current', '2012-12-31', NULL),
                ('FC009', 'Noah', 'Feldman', 'Current', '2020-06-27', NULL),
                ('FC010', 'Isabella', 'Russo', 'Current', '2019-06-12', NULL),
                ('FC011', 'Jakub', 'Pawlinski', 'Current', '2005-08-24', NULL),
                ('FC012', 'Daniel', 'Scott', 'Current', '2020-03-31', NULL),
                ('FC013', 'Gill', 'Henson', 'Current', '2010-08-16', NULL)
        """)
        
        conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15'),
                (2, 'AVLC-09436', 'ATPL', '2034-10-30'),
                (3, 'AVLC-09437', 'ATPL', '2035-09-05'),
                (4, 'AVLC-09438', 'ATPL', '2037-06-16'),
                (5, 'AVLC-09439', 'ATPL', '2031-10-29'),
                (6, 'AVLC-09440', 'ATPL', '2028-01-13'),
                (7, 'AVLC-09441', 'ATPL', '2027-06-26'),
                (8, 'AVLC-09442', 'ATPL', '2032-07-25'),
                (9, 'AVLC-09443', 'ATPL', '2028-10-24'),
                (10, 'AVLC-09444', 'ATPL', '2033-04-25')
        """)
        
        conn.execute("""
            INSERT INTO leave_bookings (staff_member_id, leave_date, leave_type)
            VALUES
                (2, '2026-01-01', 'Sick leave'),
                (7, '2026-01-01', 'Annual leave'),
                (7, '2026-01-02', 'Annual leave'),
                (13, '2026-01-07', 'Annual leave'),
                (1, '2026-01-08', 'Annual leave'),
                (6, '2026-01-08', 'Annual leave'),
                (8, '2026-01-09', 'Annual leave'),
                (4, '2026-01-13', 'Annual leave'),
                (6, '2026-01-14', 'Annual leave'),
                (4, '2026-01-18', 'Annual leave'),
                (11, '2026-01-18', 'Annual leave'),
                (1, '2026-01-19', 'Sick leave'),
                (6, '2026-01-19', 'Annual leave'),
                (9, '2026-01-19', 'Annual leave'),
                (7, '2026-01-20', 'Annual leave'),
                (8, '2026-01-22', 'Annual leave'),
                (12, '2026-01-22', 'Annual leave'),
                (2, '2026-01-25', 'Annual leave'),
                (6, '2026-01-25', 'Annual leave'),
                (2, '2026-01-28', 'Annual leave'),
                (2, '2026-01-29', 'Annual leave'),
                (5, '2026-01-30', 'Annual leave'),
                (9, '2026-01-30', 'Annual leave'),
                (13, '2026-01-30', 'Annual leave'),
                (8, '2026-01-31', 'Annual leave'),
                (8, '2026-02-01', 'Annual leave'),
                (2, '2026-02-04', 'Annual leave'),
                (10, '2026-02-04', 'Annual leave'),
                (11, '2026-02-07', 'Annual leave'),
                (13, '2026-02-07', 'Annual leave'),
                (1, '2026-02-08', 'Annual leave'),
                (7, '2026-02-09', 'Annual leave'),
                (5, '2026-02-12', 'Annual leave'),
                (9, '2026-02-12', 'Annual leave'),
                (10, '2026-02-12', 'Annual leave'),
                (6, '2026-02-13', 'Annual leave'),
                (2, '2026-02-17', 'Annual leave'),
                (5, '2026-02-17', 'Annual leave'),
                (10, '2026-02-17', 'Annual leave'),
                (2, '2026-02-19', 'Annual leave'),
                (11, '2026-02-20', 'Annual leave'),
                (1, '2026-02-21', 'Annual leave'),
                (9, '2026-02-21', 'Annual leave'),
                (9, '2026-02-27', 'Annual leave'),
                (1, '2026-03-01', 'Annual leave'),
                (4, '2026-03-01', 'Annual leave'),
                (10, '2026-03-01', 'Annual leave'),
                (12, '2026-03-01', 'Annual leave'),
                (1, '2026-03-02', 'Annual leave'),
                (1, '2026-03-03', 'Annual leave'),
                (1, '2026-03-04', 'Annual leave'),
                (1, '2026-03-05', 'Annual leave'),
                (6, '2026-03-06', 'Annual leave'),
                (6, '2026-03-07', 'Annual leave'),
                (8, '2026-03-07', 'Annual leave'),
                (7, '2026-03-08', 'Annual leave'),
                (13, '2026-03-08', 'Annual leave'),
                (13, '2026-03-09', 'Annual leave'),
                (8, '2026-03-10', 'Annual leave'),
                (13, '2026-03-10', 'Annual leave'),
                (10, '2026-03-13', 'Annual leave'),
                (10, '2026-03-14', 'Annual leave'),
                (4, '2026-03-15', 'Annual leave'),
                (10, '2026-03-15', 'Annual leave'),
                (2, '2026-03-16', 'Annual leave'),
                (4, '2026-03-16', 'Annual leave'),
                (12, '2026-03-17', 'Annual leave'),
                (9, '2026-03-19', 'Annual leave'),
                (6, '2026-03-20', 'Annual leave'),
                (5, '2026-03-21', 'Annual leave'),
                (13, '2026-03-22', 'Annual leave'),
                (2, '2026-03-25', 'Study leave'),
                (4, '2026-03-25', 'Annual leave'),
                (2, '2026-03-26', 'Study leave'),
                (1, '2026-03-27', 'Annual leave'),
                (4, '2026-03-31', 'Annual leave'),
                (6, '2026-03-31', 'Annual leave'),
                (2, '2026-04-02', 'Annual leave'),
                (11, '2026-04-05', 'Annual leave'),
                (13, '2026-04-05', 'Annual leave'),
                (11, '2026-04-07', 'Annual leave'),
                (2, '2026-04-09', 'Annual leave'),
                (9, '2026-04-09', 'Annual leave'),
                (7, '2026-04-10', 'Annual leave'),
                (11, '2026-04-10', 'Annual leave'),
                (9, '2026-04-11', 'Annual leave'),
                (11, '2026-04-11', 'Annual leave'),
                (11, '2026-04-12', 'Annual leave'),
                (7, '2026-04-13', 'Annual leave'),
                (10, '2026-04-13', 'Annual leave'),
                (5, '2026-04-16', 'Annual leave'),
                (6, '2026-04-18', 'Annual leave'),
                (9, '2026-04-18', 'Annual leave'),
                (12, '2026-04-20', 'Annual leave'),
                (1, '2026-04-22', 'Annual leave'),
                (3, '2026-04-23', 'Annual leave'),
                (4, '2026-04-23', 'Annual leave'),
                (5, '2026-04-24', 'Annual leave'),
                (7, '2026-04-24', 'Annual leave'),
                (5, '2026-04-25', 'Annual leave'),
                (7, '2026-04-25', 'Annual leave'),
                (7, '2026-04-28', 'Annual leave')
        """)
        
        conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (6, 1, 4, 1, 45, 10, 9, 'ZMY002', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived'),
                (6, 4, 1, 48, 4, 10, 9, 'ZMY013', '2026-02-01', '07:50', '2026-02-01', '11:40', '2026-02-01', '07:50', '2026-02-01', '11:45', 'Arrived'),
                (2, 1, 9, 6, 115, 9, 10, 'ZMY005', '2026-02-01', '20:20', '2026-02-01', '22:00', '2026-02-01', '20:35', '2026-02-01', '22:05', 'Arrived'),
                (2, 9, 1, 116, 11, 10, 9, 'ZMY016', '2026-02-01', '22:40', '2026-02-02', '04:15', '2026-02-01', '22:40', '2026-02-02', '04:25', 'Arrived'),
                (3, 1, 10, 6, 125, 10, 5, 'ZMY006', '2026-02-02', '08:40', '2026-02-02', '14:30', '2026-02-02', '08:40', '2026-02-02', '14:20', 'Arrived'),
                (10, 7, 1, 72, 9, 2, 8, 'ZMY015', '2026-02-02', '08:50', '2026-02-02', '11:00', '2026-02-02', '09:05', '2026-02-02', '11:00', 'Arrived'),
                (3, 10, 1, 132, 10, 5, 10, 'ZMY017', '2026-02-02', '15:10', '2026-02-02', '17:10', '2026-02-02', '15:25', '2026-02-02', '17:15', 'Arrived'),
                (4, 1, 7, 12, 88, 7, 9, 'ZMY004', '2026-02-02', '19:05', '2026-02-03', '01:00', '2026-02-02', '19:05', '2026-02-03', '01:15', 'Arrived'),
                (7, 1, 15, 9, NULL, 7, 2, 'ZMY011', '2026-02-03', '03:45', '2026-02-03', '04:45', '2026-02-03', '04:45', NULL, NULL, 'Departed'),
                (5, 1, 12, 9, NULL, 3, 9, 'ZMY008', '2026-02-03', '05:05', '2026-02-03', '09:00', NULL, NULL, NULL, NULL, 'Delayed'),
                (7, 15, 1, 232, NULL, 2, 7, 'ZMY022', '2026-02-03', '05:25', '2026-02-03', '10:25', NULL, NULL, NULL, NULL, 'Closed'),
                (1, 1, 2, 7, NULL, 5, 10, 'ZMY001', '2026-02-03', '08:00', '2026-02-03', '10:25', NULL, NULL, NULL, NULL, 'On time'),
                (5, 12, 1, 165, NULL, 9, 3, 'ZMY019', '2026-02-03', '09:40', '2026-02-03', '12:20', NULL, NULL, NULL, NULL, 'Boarding'),
                (1, 2, 1, NULL, NULL, 10, 5, 'ZMY012', '2026-02-03', '11:05', '2026-02-03', '14:10', NULL, NULL, NULL, NULL, 'Scheduled'),
                (6, 1, 11, NULL, NULL, 3, 7, 'ZMY007', '2026-02-03', '19:00', '2026-02-03', '20:30', NULL, NULL, NULL, NULL, 'Scheduled'),
                (6, 11, 1, NULL, NULL, 3, 7, 'ZMY018', '2026-02-03', '21:10', '2026-02-04', '02:05', NULL, NULL, NULL, NULL, 'Scheduled'),
                (4, 1, 13, NULL, NULL, 3, 4, 'ZMY009', '2026-02-04', '15:35', '2026-02-04', '18:25', NULL, NULL, NULL, NULL, 'Scheduled'),
                (4, 13, 1, NULL, NULL, 4, 3, 'ZMY020', '2026-02-04', '19:05', '2026-02-04', '22:30', NULL, NULL, NULL, NULL, 'Scheduled'),
                (8, 1, 5, NULL, NULL, 2, 8, 'ZMY003', '2026-02-05', '16:00', '2026-02-05', '20:00', NULL, NULL, NULL, NULL, 'Scheduled'),
                (8, 5, 1, NULL, NULL, 8, 2, 'ZMY014', '2026-02-05', '20:40', '2026-02-05', '23:50', NULL, NULL, NULL, NULL, 'Scheduled'),
                (8, 1, 14, NULL, NULL, 4, 5, 'ZMY010', '2026-02-06', '17:35', '2026-02-06', '20:40', NULL, NULL, NULL, NULL, 'Scheduled'),
                (8, 14, 1, NULL, NULL, 5, 4, 'ZMY021', '2026-02-06', '21:20', '2026-02-06', '23:15', NULL, NULL, NULL, NULL, 'Scheduled'),
                (1, 1, 9, NULL, NULL, 4, 8, 'ZMY005', '2026-02-08', '14:15', '2026-02-08', '15:25', NULL, NULL, NULL, NULL, 'Scheduled'),
                (1, 9, 1, NULL, NULL, 8, 4, 'ZMY016', '2026-02-08', '16:05', '2026-02-08', '18:40', NULL, NULL, NULL, NULL, 'Scheduled'),
                (4, 7, 1, NULL, NULL, 7, 9, 'ZMY015', '2026-02-09', '08:50', '2026-02-09', '11:00', NULL, NULL, NULL, NULL, 'Scheduled'),
                (10, 1, 7, NULL, NULL, 2, 8, 'ZMY004', '2026-02-09', '19:05', '2026-02-10', '01:00', NULL, NULL, NULL, NULL, 'Scheduled'),
                (6, 1, 12, NULL, NULL, 3, 7, 'ZMY008', '2026-02-10', '05:20', '2026-02-10', '11:00', NULL, NULL, NULL, NULL, 'Scheduled'),
                (6, 12, 1, NULL, NULL, 3, 7, 'ZMY019', '2026-02-10', '11:40', '2026-02-10', '15:15', NULL, NULL, NULL, NULL, 'Scheduled'),
                (8, 1, 9, NULL, NULL, 7, 10, 'ZMY005', '2026-02-15', '07:15', '2026-02-15', '09:00', NULL, NULL, NULL, NULL, 'Scheduled'),
                (8, 9, 1, NULL, NULL, 7, 10, 'ZMY016', '2026-02-15', '09:40', '2026-02-15', '14:45', NULL, NULL, NULL, NULL, 'Scheduled')
        """)
        
        conn.execute("""
            INSERT INTO flight_time_logs (staff_member_id, effective_date, flight_hours)
            VALUES
                (2, '2026-01-03', 9.3),
                (3, '2026-01-04', 16),
                (2, '2026-01-05', 7.4),
                (4, '2026-01-05', 8.1),
                (5, '2026-01-05', 7.6),
                (4, '2026-01-06', 8.5),
                (5, '2026-01-06', 8.5),
                (7, '2026-01-06', 18),
                (8, '2026-01-06', 7.4),
                (9, '2026-01-07', 7.3),
                (4, '2026-01-08', 8.3),
                (10, '2026-01-08', 7.6),
                (2, '2026-01-09', 4.9),
                (8, '2026-01-09', 8.3),
                (3, '2026-01-10', 5.6),
                (7, '2026-01-10', 4.6),
                (7, '2026-01-11', 5.6),
                (8, '2026-01-11', 4.9),
                (9, '2026-01-12', 4.6),
                (7, '2026-01-15', 7.5),
                (10, '2026-01-15', 7.5),
                (2, '2026-01-16', 9.3),
                (3, '2026-01-17', 16),
                (2, '2026-01-18', 7.4),
                (4, '2026-01-18', 8.1),
                (5, '2026-01-18', 7.6),
                (4, '2026-01-19', 8.5),
                (5, '2026-01-19', 8.5),
                (7, '2026-01-19', 18),
                (8, '2026-01-19', 7.4),
                (9, '2026-01-20', 7.3),
                (4, '2026-01-21', 8.3),
                (10, '2026-01-21', 7.6),
                (2, '2026-01-22', 4.9),
                (8, '2026-01-22', 8.3),
                (3, '2026-01-23', 5.6),
                (7, '2026-01-23', 4.6),
                (7, '2026-01-24', 5.6),
                (8, '2026-01-24', 4.9),
                (9, '2026-01-25', 4.6),
                (7, '2026-01-28', 7.5),
                (10, '2026-01-28', 7.5),
                (4, '2026-01-29', 3.4),
                (2, '2026-01-30', 2.1),
                (7, '2026-01-31', 5.8),
                (9, '2026-02-01', 10.5),
                (10, '2026-02-01', 13.8),
                (2, '2026-02-02', 4.1),
                (5, '2026-02-02', 8.9),
                (7, '2026-02-02', 3.6),
                (8, '2026-02-02', 4.1),
                (9, '2026-02-02', 3.6),
                (10, '2026-02-02', 8.9)
        """)
        
        conn.execute("""
            INSERT INTO flight_relief_pilots (flight_id, staff_member_id)
            VALUES
                (9, 1),
                (9, 10),
                (10, 6),
                (11, 1),
                (11, 10),
                (13, 5),
                (17, 5),
                (17, 6),
                (18, 5),
                (18, 6),
                (21, 8),
                (21, 9),
                (22, 3),
                (27, 4),
                (28, 4)
        """)
