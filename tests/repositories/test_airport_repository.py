import sqlite3
import pytest
from flightmanagement.models.airport import Airport
from flightmanagement.repositories.airport_repository import AirportRepository

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
    yield conn
    conn.close()

@pytest.fixture
def airport_repository(db_conn):
    return AirportRepository(db_conn)

@pytest.fixture
def sample_airport():
    return Airport(
        id=1,
        code="AAA",
        name="Andonovia International Airport",
        city="Andonovia",
        country="Bankantistan",
        region="Asia"
    )

class TestReadOperations:

    # READ methods
    def test_get_item_by_id_returns_airport(self, airport_repository, db_conn):
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia')
        """)

        airport = airport_repository.get_item_by_id(1)

        assert airport is not None
        assert airport.id == 1
        assert airport.code == "AAA"

    def test_get_item_by_id_returns_none_when_missing(self, airport_repository):
        assert airport_repository.get_item_by_id(999) is None

    def test_get_item_by_code_returns_airport(self, airport_repository, db_conn):
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia')
        """)

        airport = airport_repository.get_item_by_code("AAA")

        assert airport is not None
        assert airport.code == "AAA"

    def test_get_item_by_code_returns_none_when_missing(self, airport_repository):
        assert airport_repository.get_item_by_code("UNK") is None

class TestListOperations:

    def test_get_airport_list_returns_sorted_list(self, airport_repository, db_conn):
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES
                ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia'),
                ('BBB', 'Boronia International Airport', 'Boronia', 'Charmania', 'Europe')
        """)

        airport_list = airport_repository.get_airport_list()

        assert len(airport_list) == 2
        assert airport_list[0].code == "AAA"
        assert airport_list[1].code == "BBB"

    def test_get_airport_list_returns_none_when_empty(self, airport_repository):
        assert airport_repository.get_airport_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, airport_repository, db_conn):
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES
                ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia'),
                ('BBB', 'Boronia International Airport', 'Boronia', 'Bankantistan', 'Europe')
        """)

        results = airport_repository.search_on_field("country", "Bankantistan")

        assert len(results) == 2
        assert all(a.country == "Bankantistan" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, airport_repository):
        assert airport_repository.search_on_field("country", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, airport_repository):
        with pytest.raises(Exception):
            airport_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_item_persists_to_db(self, airport_repository, db_conn, sample_airport):
        airport_repository.insert_item(sample_airport)

        row = db_conn.execute(
            "SELECT * FROM airport WHERE code = 'AAA'"
        ).fetchone()

        assert row is not None
        assert row["country"] == "Bankantistan"

    def test_insert_item_prevents_duplicates(self, airport_repository, db_conn, sample_airport): # TODO - add better exception handling for any uniqueness constraints
        airport_repository.insert_item(sample_airport)

        with pytest.raises(sqlite3.IntegrityError):
            airport_repository.insert_item(sample_airport)

    def test_update_item_updates_fields(self, airport_repository, db_conn):
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES
                ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia')
        """)

        updated = Airport(
            id=1,
            code="AAA",
            name="Andonovia International Airport",
            city="Zimfantown",
            country="Yankovia",
            region="Europe"
        )
        airport_repository.update_item(updated)

        row = db_conn.execute("SELECT * FROM airport WHERE id = 1").fetchone()
        assert row["city"] == "Zimfantown"
        assert row["country"] == "Yankovia"
        assert row["region"] == "Europe"

    def test_update_item_prevents_duplicates(self, airport_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES
                ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia'),
                ('BBB', 'Boronia International Airport', 'Boronia', 'Bankantistan', 'Europe')
        """)

        updated = Airport(
            id=1,
            code="BBB",
            name="Andonovia International Airport",
            city="Zimfantown",
            country="Yankovia",
            region="Europe"
        )

        with pytest.raises(sqlite3.IntegrityError):
            airport_repository.update_item(updated)

    def test_delete_item_removes_row(self, airport_repository, db_conn, sample_airport):
        db_conn.execute("""
            INSERT INTO airport (code, name, city, country, region)
            VALUES
                ('AAA', 'Andonovia International Airport', 'Andonovia', 'Bankantistan', 'Asia')
        """)

        airport_repository.delete_item(sample_airport)

        row = db_conn.execute("SELECT * FROM airport WHERE id = 1").fetchone()
        assert row is None

