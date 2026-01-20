import sqlite3
import pytest
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.repositories.aircraft_repository import AircraftRepository

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
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
    yield conn
    conn.close()

@pytest.fixture
def aircraft_repository(db_conn):
    return AircraftRepository(db_conn)

@pytest.fixture
def sample_aircraft():
    return Aircraft(
        id=None,
        registration="G-ABCD",
        manufacturer_serial_no=269785,
        icao_hex="406ABC",
        manufacturer="Boeing",
        model="737",
        icao_type="B737",
        status="Active"
    )

# READ methods
def test_get_by_id_returns_aircraft(aircraft_repository, db_conn):
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES ('G-TEST', 269785, 'ABC123', 'Airbus', 'A320', 'A320', 'Active')
    """)

    aircraft = aircraft_repository.get_by_id(1)

    assert aircraft is not None
    assert aircraft.id == 1
    assert aircraft.registration == "G-TEST"

def test_get_by_id_returns_none_when_missing(aircraft_repository):
    assert aircraft_repository.get_by_id(999) is None

def test_get_by_registration_returns_aircraft(aircraft_repository, db_conn):
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES ('G-REG1', 56765, 'DEF456', 'Boeing', '747', 'B744', 'Active')
    """)

    aircraft = aircraft_repository.get_by_registration("G-REG1")

    assert aircraft is not None
    assert aircraft.registration == "G-REG1"

def test_get_by_registration_returns_none_when_missing(aircraft_repository):
    assert aircraft_repository.get_by_registration("UNKNOWN") is None

# LIST methods
def test_get_aircraft_list_returns_sorted_list(aircraft_repository, db_conn):
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES 
            ('G-REG1', 56765, 'DEF456', 'Boeing', '747', 'B744', 'Active'),
            ('G-REG2', 56766, 'DEF457', 'Airbus', 'A320', 'A320', 'Active')
    """)

    aircraft_list = aircraft_repository.get_aircraft_list()

    assert len(aircraft_list) == 2
    assert aircraft_list[0].registration == "G-REG1"
    assert aircraft_list[1].registration == "G-REG2"

def test_get_aircraft_list_returns_none_when_empty(aircraft_repository):
    assert aircraft_repository.get_aircraft_list() == []

# SEARCH methods
def test_search_on_field_returns_matches(aircraft_repository, db_conn):
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES 
            ('G-ONE', 1, '1', 'Boeing', '737', 'B737', 'Active'),
            ('G-TWO', 2, '2', 'Boeing', '747', 'B744', 'Active')
    """)

    results = aircraft_repository.search_on_field("manufacturer", "Boeing")

    assert len(results) == 2
    assert all(a.manufacturer == "Boeing" for a in results)

def test_search_on_field_returns_none_when_no_matches(aircraft_repository):
    assert aircraft_repository.search_on_field("manufacturer", "Unknown") == []

def test_search_on_field_invalid_column_raises_error(aircraft_repository):
    with pytest.raises(Exception):
        aircraft_repository.search_on_field("invalid_column", "value")

# WRITE methods
def test_add_aircraft_persists_to_db(aircraft_repository, db_conn, sample_aircraft):
    aircraft_repository.add_aircraft(sample_aircraft)

    row = db_conn.execute(
        "SELECT * FROM aircraft WHERE registration = 'G-ABCD'"
    ).fetchone()

    assert row is not None
    assert row["manufacturer"] == "Boeing"

def test_add_aircraft_prevents_duplicates(aircraft_repository, db_conn, sample_aircraft): # TODO - add better exception handling for any uniqueness constraints
    aircraft_repository.add_aircraft(sample_aircraft)

    with pytest.raises(sqlite3.IntegrityError):
        aircraft_repository.add_aircraft(sample_aircraft)

    row = db_conn.execute(
        "SELECT COUNT(*) FROM aircraft WHERE registration = 'G-ABCD'"
    ).fetchone()

    assert row[0] == 1

def test_update_aircraft_updates_fields(aircraft_repository, db_conn):
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES ('G-UPD', 3456, 'HEX', 'Old', 'Old', 'OLD', 'Inactive')
    """)

    updated = Aircraft(
        id=1,
        registration="G-UPD",
        manufacturer_serial_no=3456,
        icao_hex="HEX",
        manufacturer="New",
        model="New",
        icao_type="NEW",
        status="Active"
    )

    aircraft_repository.update_aircraft(updated)

    row = db_conn.execute("SELECT * FROM aircraft WHERE id = 1").fetchone()
    assert row["manufacturer"] == "New"
    assert row["status"] == "Active"

def test_update_aircraft_prevents_duplicates(aircraft_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES ('G-TEST1', 3456, 'HEX', 'Airbus', 'A320', 'A320', 'Inactive')
    """)

    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES ('G-TEST2', 3457, 'HEX2', 'Airbus', 'A320', 'A320', 'Inactive')
    """)

    updated = Aircraft(
            id=1,
            registration="G-TEST2",
            manufacturer_serial_no=3457,
            icao_hex="HEX2",
            manufacturer="Airbus",
            model="A320",
            icao_type="A320",
            status="Inactive"
        )

    with pytest.raises(sqlite3.IntegrityError):
        aircraft_repository.update_aircraft(updated)

    row = db_conn.execute(
        "SELECT COUNT(*) FROM aircraft WHERE registration = 'G-TEST2'"
    ).fetchone()

    assert row[0] == 1

def test_delete_aircraft_removes_row(aircraft_repository, db_conn):
    db_conn.execute("""
        INSERT INTO aircraft (registration, manufacturer_serial_no, icao_hex, manufacturer, model, icao_type, status)
        VALUES ('G-DEL', 1234, 'HEX', 'M', 'M', 'T', 'Active')
    """)

    aircraft_repository.delete_aircraft(1)

    row = db_conn.execute("SELECT * FROM aircraft WHERE id = 1").fetchone()
    assert row is None

