import sqlite3
import pytest
from flightmanagement.error import UniqueConstraintViolation
from flightmanagement.db.db import initialise_schema
from flightmanagement.models.location import Location
from flightmanagement.repositories.location_repository import LocationRepository

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    initialise_schema(conn)
    yield conn
    conn.close()

@pytest.fixture
def location_repository(db_conn):
    return LocationRepository(db_conn)

@pytest.fixture
def sample_location():
    return Location(
        location_id=1,
        location_type="Airport",
        icao_location_code="ABCD",
        iata_airport_code="ABC",
        location_name="Test Airport",
        town_or_city="Milton Keynes",
        state_or_county="Buckinghamshire",
        country="United Kingdom",
        geographic_region="Europe",
        decimal_latitude=-45.30,
        decimal_longitude=112.30
    )

class TestReadOperations:

    # READ methods
    def test_get_location_by_id_returns_location(self, location_repository, db_conn):
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619)
        """)

        location = location_repository.get_location_by_id(1)

        assert location is not None
        assert location.location_id == 1
        assert location.iata_airport_code == "LHR"

    def test_get_location_by_id_returns_none_when_missing(self, location_repository):
        assert location_repository.get_location_by_id(999) is None

    def test_get_location_by_code_returns_location(self, location_repository, db_conn):
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619)
        """)

        location = location_repository.get_location_by_code("LHR")

        assert location is not None
        assert location.iata_airport_code == "LHR"

    def test_get_location_by_code_returns_none_when_missing(self, location_repository):
        assert location_repository.get_location_by_code("UNK") is None

class TestListOperations:

    def test_get_location_list_returns_sorted_list(self, location_repository, db_conn):
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619),
                ('Airport', 'EGKK', 'LGW', 'London Gatwick Airport', 'London', 'West Sussex', 'United Kingdom', 'Europe', 51.1537, -0.1821)
        """)

        location_list = location_repository.get_location_list()

        assert len(location_list) == 2
        assert location_list[0].iata_airport_code == "LGW"
        assert location_list[1].iata_airport_code == "LHR"

    def test_get_location_list_returns_none_when_empty(self, location_repository):
        assert location_repository.get_location_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, location_repository, db_conn):
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619),
                ('Airport', 'EGKK', 'LGW', 'London Gatwick Airport', 'London', 'West Sussex', 'United Kingdom', 'Europe', 51.1537, -0.1821)
        """)

        results = location_repository.search_on_field("country", "United Kingdom")

        assert len(results) == 2
        assert all(a.country == "United Kingdom" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, location_repository):
        assert location_repository.search_on_field("country", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, location_repository):
        with pytest.raises(Exception):
            location_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_location_persists_to_db(self, location_repository, db_conn, sample_location):
        location_repository.insert_location(sample_location)

        row = db_conn.execute(
            "SELECT * FROM locations WHERE iata_airport_code = 'ABC'"
        ).fetchone()

        assert row is not None
        assert row["country"] == "United Kingdom"

    def test_insert_location_prevents_duplicates(self, location_repository, db_conn, sample_location):
        location_repository.insert_location(sample_location)

        with pytest.raises(UniqueConstraintViolation):
            location_repository.insert_location(sample_location)

    def test_update_location_updates_fields(self, location_repository, db_conn):
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619)
        """)

        updated = Location(
            location_id=1,
            location_type="Airport",
            icao_location_code="ABCD",
            iata_airport_code="ABC",
            location_name="Test Airport",
            town_or_city="Milton Keynes",
            state_or_county="Buckinghamshire",
            country="United Kingdom",
            geographic_region="Europe",
            decimal_latitude=-45.30,
            decimal_longitude=112.30
        )
        location_repository.update_location(updated)

        row = db_conn.execute("SELECT * FROM locations WHERE location_id = 1").fetchone()

        assert row["location_id"] == 1
        assert row["location_type"] == "Airport"
        assert row["icao_location_code"] == "ABCD"
        assert row["iata_airport_code"] == "ABC"
        assert row["location_name"] == "Test Airport"
        assert row["town_or_city"] == "Milton Keynes"
        assert row["state_or_county"] == "Buckinghamshire"
        assert row["country"] == "United Kingdom"
        assert row["geographic_region"] == "Europe"
        assert row["decimal_latitude"] == -45.30
        assert row["decimal_longitude"] == 112.30

    def test_update_item_prevents_duplicates(self, location_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619),
                ('Airport', 'EGKK', 'LGW', 'London Gatwick Airport', 'London', 'West Sussex', 'United Kingdom', 'Europe', 51.1537, -0.1821)
        """)

        updated = Location(
            location_id=1,
            location_type="Airport",
            icao_location_code="EGKK",
            iata_airport_code="LGW",
            location_name="London Heathrow Airport",
            town_or_city="London",
            state_or_county="Greater London",
            country="United Kingdom",
            geographic_region="Europe",
            decimal_latitude=51.4706,
            decimal_longitude=-0.1821
        )

        with pytest.raises(UniqueConstraintViolation):
            location_repository.update_location(updated)

    def test_delete_item_removes_row(self, location_repository, db_conn, sample_location):
        db_conn.execute("""
            INSERT INTO locations (location_type, icao_location_code, iata_airport_code, location_name, town_or_city, state_or_county, country, geographic_region, decimal_latitude, decimal_longitude)
            VALUES
                ('Airport', 'EGLL', 'LHR', 'London Heathrow Airport', 'London', 'Greater London', 'United Kingdom', 'Europe', 51.4706, -0.4619)
        """)

        location_repository.delete_location(sample_location)

        row = db_conn.execute("SELECT * FROM locations WHERE location_id = 1").fetchone()
        assert row is None

