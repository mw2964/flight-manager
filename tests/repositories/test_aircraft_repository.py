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
        aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
        aircraft_type_id INTEGER NOT NULL REFERENCES aircraft_types(aircraft_type_id) ON DELETE RESTRICT,
        registration TEXT NOT NULL UNIQUE,
        manufacturer_serial_no INTEGER UNIQUE,
        icao_hex TEXT UNIQUE,
        aircraft_status TEXT CHECK(aircraft_status IN ('Active', 'Inactive', 'Decommissioned'))
    )
    """)
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
        CREATE VIEW IF NOT EXISTS vw_aircraft AS
            SELECT *
            FROM aircraft
            NATURAL JOIN aircraft_types;
    """)
    yield conn
    conn.close()

@pytest.fixture
def aircraft_repository(db_conn):
    return AircraftRepository(db_conn)

@pytest.fixture
def sample_aircraft():
    return Aircraft(
        aircraft_id=1,
        aircraft_type_id=1,
        registration="G-ABCD",
        manufacturer_serial_no=269785,
        icao_hex="406ABC",
        aircraft_status="Active"
    )

class TestReadOperations:

    # READ methods
    def test_get_aircraft_by_id_returns_aircraft(self, aircraft_repository, db_conn):
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES (1, 'G-TEST', 269785, 'ABC123', 'Active')
        """)

        aircraft = aircraft_repository.get_aircraft_by_id(1)

        assert aircraft is not None
        assert aircraft.aircraft_id == 1
        assert aircraft.registration == "G-TEST"

    def test_get_aircraft_by_id_returns_none_when_missing(self, aircraft_repository):
        assert aircraft_repository.get_aircraft_by_id(999) is None

    def test_get_aircraft_by_registration_returns_aircraft(self, aircraft_repository, db_conn):
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES (1, 'G-TEST', 269785, 'ABC123', 'Active')
        """)

        aircraft = aircraft_repository.get_aircraft_by_registration("G-TEST")

        assert aircraft is not None
        assert aircraft.registration == "G-TEST"

    def test_get_aircraft_by_registration_returns_none_when_missing(self, aircraft_repository):
        assert aircraft_repository.get_aircraft_by_registration("UNKNOWN") is None

class TestListOperations:

    def test_get_aircraft_list_returns_sorted_list(self, aircraft_repository, db_conn):
        db_conn.execute("""
            INSERT INTO aircraft_types (manufacturer, model, icao_type)
            VALUES
                ('TestManufacturer1', 'TestModel1', 'Test1'),
                ('TestManufacturer2', 'TestModel2', 'Test2')                        
        """)
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (1, 'G-TEST1', 269785, 'ABC123', 'Active'),
                (2, 'G-TEST2', 269786, 'ABC124', 'Inactive')                        
        """)

        aircraft_list = aircraft_repository.get_aircraft_list()

        assert len(aircraft_list) == 2
        assert aircraft_list[0]["registration"] == "G-TEST1"
        assert aircraft_list[1]["registration"] == "G-TEST2"

    def test_get_aircraft_list_returns_none_when_empty(self, aircraft_repository):
        assert aircraft_repository.get_aircraft_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, aircraft_repository, db_conn):
        db_conn.execute("""
            INSERT INTO aircraft_types (manufacturer, model, icao_type)
            VALUES
                ('TestManufacturer1', 'TestModel1', 'Test1'),
                ('TestManufacturer2', 'TestModel2', 'Test2')                        
        """)
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (1, 'G-TEST1', 269785, 'ABC123', 'Active'),
                (2, 'G-TEST2', 269786, 'ABC124', 'Active')                        
        """)

        results = aircraft_repository.search_aircraft_on_field("aircraft_status", "Active")

        assert len(results) == 2
        assert all(a["aircraft_status"] == "Active" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, aircraft_repository):
        assert aircraft_repository.search_aircraft_on_field("aircraft_status", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, aircraft_repository):
        with pytest.raises(Exception):
            aircraft_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_aircraft_persists_to_db(self, aircraft_repository, db_conn, sample_aircraft):
        aircraft_repository.insert_aircraft(sample_aircraft)

        row = db_conn.execute(
            "SELECT * FROM aircraft WHERE registration = 'G-ABCD'"
        ).fetchone()

        assert row is not None
        assert row["manufacturer_serial_no"] == 269785

    def test_insert_aircraft_prevents_duplicates(self, aircraft_repository, db_conn, sample_aircraft): # TODO - add better exception handling for any uniqueness constraints
        aircraft_repository.insert_aircraft(sample_aircraft)

        with pytest.raises(sqlite3.IntegrityError):
            aircraft_repository.insert_aircraft(sample_aircraft)

    def test_update_aircraft_updates_fields(self, aircraft_repository, db_conn):
        db_conn.execute("""
            INSERT INTO aircraft_types (manufacturer, model, icao_type)
            VALUES
                ('TestManufacturer1', 'TestModel1', 'Test1'),
                ('TestManufacturer2', 'TestModel2', 'Test2')                     
        """)
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (1, 'G-TEST1', 269785, 'ABC123', 'Active')                      
        """)

        updated = Aircraft(
            aircraft_id = 1,
            aircraft_type_id = 2,
            registration = "G-UPD",
            manufacturer_serial_no = 3456,
            icao_hex = "HEX",
            aircraft_status="Inactive"
        )

        aircraft_repository.update_aircraft(updated)

        row = db_conn.execute("SELECT * FROM aircraft WHERE aircraft_id = 1").fetchone()
        assert row["registration"] == "G-UPD"
        assert row["aircraft_status"] == "Inactive"

    def test_update_item_prevents_duplicates(self, aircraft_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
        db_conn.execute("""
            INSERT INTO aircraft_types (manufacturer, model, icao_type)
            VALUES
                ('TestManufacturer1', 'TestModel1', 'Test1')                     
        """)
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (1, 'G-TEST1', 3456, 'HEX', 'Inactive'),
                (1, 'G-TEST2', 3457, 'HEX2', 'Inactive')
        """)

        updated = Aircraft(
                aircraft_id=1,
                aircraft_type_id=1,
                registration="G-TEST2",
                manufacturer_serial_no=3457,
                icao_hex="HEX2",
                aircraft_status="Inactive"
            )

        with pytest.raises(sqlite3.IntegrityError):
            aircraft_repository.update_aircraft(updated)

    def test_delete_aircraft_removes_row(self, aircraft_repository, db_conn, sample_aircraft):
        db_conn.execute("""
            INSERT INTO aircraft_types (manufacturer, model, icao_type)
            VALUES
                ('TestManufacturer1', 'TestModel1', 'Test1')                     
        """)
        db_conn.execute("""
            INSERT INTO aircraft (aircraft_type_id, registration, manufacturer_serial_no, icao_hex, aircraft_status)
            VALUES
                (1, 'G-TEST1', 3456, 'HEX', 'Inactive')
        """)

        aircraft_repository.delete_aircraft(sample_aircraft)

        row = db_conn.execute("SELECT * FROM aircraft WHERE aircraft_id = 1").fetchone()
        assert row is None

