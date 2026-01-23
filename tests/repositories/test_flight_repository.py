import sqlite3
import pytest
from datetime import datetime
from flightmanagement.models.flight import Flight
from flightmanagement.repositories.flight_repository import FlightRepository

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
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
            FOREIGN KEY(copilot_id) REFERENCES pilot(id),
            UNIQUE(flight_number, departure_time_scheduled)
        )
    """)
    yield conn
    conn.close()

@pytest.fixture
def flight_repository(db_conn):
    return FlightRepository(db_conn)

@pytest.fixture
def sample_flight():
    return Flight(
        id=1,
        flight_number="ZMY123",
        aircraft_id=1,
        origin_id=1,
        destination_id=2,
        pilot_id=1,
        copilot_id=2,
        departure_time_scheduled=datetime(2026, 1, 1, 15, 30),
        arrival_time_scheduled=datetime(2026, 1, 1, 16, 55),
        departure_time_actual=datetime(2026, 1, 2, 15, 30),
        arrival_time_actual=datetime(2026, 1, 2, 16, 50),
        status="Arrived"
    )

@pytest.fixture
def test_pilot_sql():
    return """
        INSERT INTO pilot (first_name, family_name)
        VALUES ('Andrea', 'Almond')
    """

@pytest.fixture
def test_airport_sql():
    return """
        INSERT INTO airport (code, name, city, country, region)
        VALUES
            ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia'),
            ('BBB', 'Boronia International Airport', 'Boronia', 'Bankantistan', 'Europe')
    """

@pytest.fixture
def test_aircraft_sql():
    return """
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES 
            ('G-REG1', 56765, 'DEF456', 'Boeing', '747', 'B744', 'Active'),
            ('G-REG2', 56766, 'DEF457', 'Airbus', 'A320', 'A320', 'Active')
    """

class TestReadOperations:

    # READ methods
    def test_get_item_by_id_returns_flight(self, flight_repository, db_conn):
        db_conn.execute("""
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES ('ZMY123', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived')
        """)

        flight = flight_repository.get_item_by_id(1)

        assert flight is not None
        assert flight.id == 1
        assert flight.flight_number == "ZMY123"

    def test_get_item_by_id_returns_none_when_missing(self, flight_repository):
        assert flight_repository.get_item_by_id(999) is None

class TestListOperations:

    def test_get_flight_list_returns_sorted_list(self, flight_repository, db_conn):
        db_conn.execute("""
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES 
                ('ZMY123', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived'),
                ('ZMY234', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived')
        """)
        flight_list = flight_repository.get_flight_list()

        assert len(flight_list) == 2
        assert flight_list[0].flight_number == "ZMY123"
        assert flight_list[1].flight_number == "ZMY234"

    def test_get_flight_list_returns_none_when_empty(self, flight_repository):
        assert flight_repository.get_flight_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, flight_repository, db_conn):
        db_conn.execute("""
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES 
                ('ZMY123', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived'),
                ('ZMY234', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived')
        """)

        results = flight_repository.search_on_field("status", "Arrived")

        assert len(results) == 2
        assert all(a.status == "Arrived" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, flight_repository):
        assert flight_repository.search_on_field("status", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, flight_repository):
        with pytest.raises(Exception):
            flight_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_item_persists_to_db(self, flight_repository, db_conn, sample_flight):
        flight_repository.insert_item(sample_flight)

        row = db_conn.execute(
            "SELECT * FROM flight WHERE flight_number = 'ZMY123'"
        ).fetchone()

        assert row is not None
        assert row["flight_number"] == "ZMY123"

    def test_insert_item_prevents_duplicates(self, flight_repository, db_conn, sample_flight): # TODO - add better exception handling for any uniqueness constraints
        flight_repository.insert_item(sample_flight)

        with pytest.raises(sqlite3.IntegrityError):
            flight_repository.insert_item(sample_flight)

    def test_update_item_updates_fields(self, flight_repository, db_conn):
        db_conn.execute("""
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES ('ZMY123', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived')
        """)

        updated = Flight(
            id=1,
            flight_number="ZMY234",
            aircraft_id=1,
            origin_id=2,
            destination_id=1,
            pilot_id=2,
            copilot_id=1,
            departure_time_scheduled=datetime(2027, 2, 2, 16, 40),
            arrival_time_scheduled=datetime(2027, 2, 2, 17, 50),
            departure_time_actual=datetime(2027, 2, 3, 16, 40),
            arrival_time_actual=datetime(2027, 2, 3, 17, 55),
            status="Delayed"
        )

        flight_repository.update_item(updated)

        row = db_conn.execute("SELECT * FROM flight WHERE id = 1").fetchone()
        assert row["flight_number"] == "ZMY234"
        assert row["aircraft_id"] == 1
        assert row["origin_id"] == 2
        assert row["destination_id"] == 1
        assert row["pilot_id"] == 2
        assert row["copilot_id"] == 1
        assert row["departure_time_scheduled"] == "2027-02-02 16:40"
        assert row["arrival_time_scheduled"] == "2027-02-02 17:50"
        assert row["departure_time_actual"] == "2027-02-03 16:40"
        assert row["arrival_time_actual"] == "2027-02-03 17:55"
        assert row["status"] == "Delayed"

    def test_update_item_prevents_duplicates(self, flight_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
        db_conn.execute("""
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES 
                ('ZMY123', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived'),
                ('ZMY234', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived')
        """)

        updated = Flight(
            id=1,
            flight_number="ZMY234",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            pilot_id=1,
            copilot_id=2,
            departure_time_scheduled=datetime(2026, 1, 1, 15, 30),
            arrival_time_scheduled=datetime(2026, 1, 1, 16, 55),
            departure_time_actual=datetime(2026, 1, 2, 15, 30),
            arrival_time_actual=datetime(2026, 1, 2, 16, 50),
            status="Arrived"
        )

        with pytest.raises(sqlite3.IntegrityError):
            flight_repository.update_item(updated)

    def test_delete_item_removes_row(self, flight_repository, db_conn, sample_flight):
        db_conn.execute("""
            INSERT INTO flight (flight_number, aircraft_id, origin_id, destination_id, pilot_id, copilot_id, departure_time_scheduled, arrival_time_scheduled, departure_time_actual, arrival_time_actual, status)
            VALUES ('ZMY123', 1, 1, 2, 1, 2, '2026-01-01 15:30', '2026-01-01 16:55', '2026-01-02 15:30', '2026-01-02 16:50', 'Arrived')
        """)
        flight_repository.delete_item(sample_flight)

        row = db_conn.execute("SELECT * FROM flight WHERE id = 1").fetchone()
        assert row is None

