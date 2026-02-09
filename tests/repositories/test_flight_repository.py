import sqlite3
import pytest
from datetime import date, time
from flightmanagement.error import UniqueConstraintViolation
from flightmanagement.db.db import initialise_schema
from flightmanagement.models.flight import Flight
from flightmanagement.repositories.flight_repository import FlightRepository

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    initialise_schema(conn)
    yield conn
    conn.close()

@pytest.fixture
def flight_repository(db_conn):
    return FlightRepository(db_conn)

@pytest.fixture
def sample_flight():
    return Flight(
        flight_id=1,
        flight_number="ZMY123",
        aircraft_id=1,
        origin_location_id=1,
        departure_gate_id=1,
        destination_location_id=2,
        arrival_gate_id=2,
        captain_id=1,
        first_officer_id=2,
        scheduled_departure_date=date(2026, 1, 1),
        scheduled_departure_time=time(15, 30),
        scheduled_arrival_date=date(2026, 1, 1),
        scheduled_arrival_time=time(16, 55),
        confirmed_departure_date=date(2026, 1, 2),
        confirmed_departure_time=time(15, 30),
        confirmed_arrival_date=date(2026, 1, 2),
        confirmed_arrival_time=time(16, 50),
        flight_status="Arrived"
    )

@pytest.fixture
def insert_test_data(db_conn):
    db_conn.execute(test_staff_sql())
    db_conn.execute(test_pilot_sql())
    db_conn.execute(test_location_sql())
    db_conn.execute(test_terminal_sql())
    db_conn.execute(test_gate_sql())
    db_conn.execute(test_aircraft_type_sql())
    db_conn.execute(test_aircraft_sql())

def test_staff_sql():
    return """
        INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Morrison', 'Current', '2014-04-13', NULL),
                ('FC002', 'Emily', 'Carter', 'Current', '2021-10-23', NULL)
    """

def test_pilot_sql():
    return """
        INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15'),
                (2, 'AVLC-09436', 'ATPL', '2034-10-30')
    """

def test_location_sql():
    return """
        INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619),
                ('Airport', 'EGKK', 'LGW', 'London Gatwick Airport', 'London', 'West Sussex', 'United Kingdom', 'Europe', 51.1537, -0.1821)
    """

def test_terminal_sql():
    return """
        INSERT INTO terminals (location_id, terminal_name)
            VALUES
                (1, 'Terminal 2'),
                (2, 'Terminal 3')
    """

def test_gate_sql():
    return """
        INSERT INTO gates (terminal_id, gate_number)
            VALUES
                (1, '1'),
                (2, '2')
    """

def test_aircraft_sql():
    return """
        INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
        VALUES
            (1, 'G-TEST1', 269785, 'ABC123', 'Active'),
            (2, 'G-TEST2', 269786, 'ABC124', 'Active')
    """

def test_aircraft_type_sql():
    return """
        INSERT INTO aircraft_types (manufacturer, model, icao_type)
        VALUES
            ('TestManufacturer1', 'TestModel1', 'Test1'),
            ('TestManufacturer2', 'TestModel2', 'Test2')                        
    """

class TestReadOperations:

    # READ methods
    def test_get_flight_by_id_returns_flight(self, flight_repository, db_conn, insert_test_data):
        db_conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (1, 1, 2, 1, 2, 1, 2, 'ZMY123', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived')
        """)

        flight = flight_repository.get_flight_by_id(1)

        assert flight is not None
        assert flight.flight_id == 1
        assert flight.flight_number == "ZMY123"

    def test_get_flight_by_id_returns_none_when_missing(self, flight_repository):
        assert flight_repository.get_flight_by_id(999) is None

class TestListOperations:

    def test_get_flight_list_returns_sorted_list(self, flight_repository, db_conn, insert_test_data):
        db_conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (1, 1, 2, 1, 2, 1, 2, 'ZMY123', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived'),
                (1, 1, 2, 1, 2, 1, 2, 'ZMY234', '2026-02-01', '07:50', '2026-02-01', '11:40', '2026-02-01', '07:50', '2026-02-01', '11:45', 'Arrived')
        """)
        flight_list = flight_repository.get_flight_list()

        assert len(flight_list) == 2
        assert flight_list[0].flight_number == "ZMY234"
        assert flight_list[1].flight_number == "ZMY123"

    def test_get_flight_list_returns_none_when_empty(self, flight_repository):
        assert flight_repository.get_flight_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, flight_repository, db_conn, insert_test_data):
        db_conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (1, 1, 2, 1, 2, 1, 2, 'ZMY123', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived'),
                (1, 1, 2, 1, 2, 1, 2, 'ZMY234', '2026-02-01', '07:50', '2026-02-01', '11:40', '2026-02-01', '07:50', '2026-02-01', '11:45', 'Arrived')
        """)

        results = flight_repository.search_on_field("flight_status", "Arrived")

        assert len(results) == 2
        assert all(a['flight_status'] == "Arrived" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, flight_repository):
        assert flight_repository.search_on_field("flight_status", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, flight_repository):
        with pytest.raises(Exception):
            flight_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_flight_persists_to_db(self, flight_repository, db_conn, sample_flight, insert_test_data):
        flight_repository.insert_flight(sample_flight)

        row = db_conn.execute(
            "SELECT * FROM flights WHERE flight_number = 'ZMY123'"
        ).fetchone()

        assert row is not None
        assert row["flight_number"] == "ZMY123"

    def test_insert_flight_prevents_duplicates(self, flight_repository, sample_flight, insert_test_data): # TODO - add better exception handling for any uniqueness constraints
        flight_repository.insert_flight(sample_flight)

        with pytest.raises(UniqueConstraintViolation):
            flight_repository.insert_flight(sample_flight)

    def test_update_flight_updates_fields(self, flight_repository, db_conn, insert_test_data):
        db_conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (1, 1, 2, 1, 2, 1, 2, 'ZMY123', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived')
        """)

        updated = Flight(
            flight_id=1,
            flight_number="ZMY234",
            aircraft_id=1,
            origin_location_id=1,
            departure_gate_id=1,
            destination_location_id=2,
            arrival_gate_id=2,
            captain_id=1,
            first_officer_id=2,
            scheduled_departure_date=date(2026, 1, 1),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 1),
            scheduled_arrival_time=time(16, 55),
            confirmed_departure_date=date(2026, 1, 2),
            confirmed_departure_time=time(15, 30),
            confirmed_arrival_date=date(2026, 1, 2),
            confirmed_arrival_time=time(16, 50),
            flight_status="Delayed"
        )

        flight_repository.update_flight(updated)

        row = db_conn.execute("SELECT * FROM flights WHERE flight_id = 1").fetchone()
        assert row["flight_number"] == "ZMY234"
        assert row["aircraft_id"] == 1
        assert row["origin_location_id"] == 1
        assert row["departure_gate_id"] == 1
        assert row["destination_location_id"] == 2
        assert row["arrival_gate_id"] == 2
        assert row["captain_id"] == 1
        assert row["first_officer_id"] == 2
        assert row["scheduled_departure_date"] == "2026-01-01"
        assert row["scheduled_departure_time"] == "15:30"
        assert row["scheduled_arrival_date"] == "2026-01-01"
        assert row["scheduled_arrival_time"] == "16:55"
        assert row["confirmed_departure_date"] == "2026-01-02"
        assert row["confirmed_departure_time"] == "15:30"
        assert row["confirmed_arrival_date"] == "2026-01-02"
        assert row["confirmed_arrival_time"] == "16:50"
        assert row["flight_status"] == "Delayed"

    def test_update_item_prevents_duplicates(self, flight_repository, db_conn, insert_test_data):
        db_conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (1, 1, 2, 1, 2, 1, 2, 'ZMY123', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived'),
                (1, 1, 2, 1, 2, 1, 2, 'ZMY234', '2026-02-01', '07:50', '2026-02-01', '11:40', '2026-02-01', '07:50', '2026-02-01', '11:45', 'Arrived')
        """)

        updated = Flight(
            flight_id=1,
            flight_number="ZMY234",
            aircraft_id=1,
            origin_location_id=1,
            destination_location_id=2,
            departure_gate_id=1,            
            arrival_gate_id=2,
            captain_id=1,
            first_officer_id=2,
            scheduled_departure_date=date(2026, 2, 1),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 2, 1),
            scheduled_arrival_time=time(16, 55),
            confirmed_departure_date=date(2026, 1, 2),
            confirmed_departure_time=time(15, 30),
            confirmed_arrival_date=date(2026, 1, 2),
            confirmed_arrival_time=time(16, 50),
            flight_status="Delayed"
        )

        with pytest.raises(UniqueConstraintViolation):
            flight_repository.update_flight(updated)

    def test_delete_item_removes_row(self, flight_repository, db_conn, sample_flight, insert_test_data):
        db_conn.execute("""
            INSERT INTO flights (aircraft_id, origin_location_id, destination_location_id, departure_gate_id, arrival_gate_id, captain_id, first_officer_id, flight_number, scheduled_departure_date, scheduled_departure_time, scheduled_arrival_date, scheduled_arrival_time, confirmed_departure_date, confirmed_departure_time, confirmed_arrival_date, confirmed_arrival_time, flight_status)
            VALUES
                (1, 1, 2, 1, 2, 1, 2, 'ZMY123', '2026-02-01', '03:15', '2026-02-01', '07:10', '2026-02-01', '03:30', '2026-02-01', '07:10', 'Arrived')
        """)
        flight_repository.delete_flight(sample_flight)

        row = db_conn.execute("SELECT * FROM flights WHERE flight_id = 1").fetchone()
        assert row is None

