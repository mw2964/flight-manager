import sqlite3
import pytest
from flightmanagement.models.pilot import Pilot
from flightmanagement.repositories.pilot_repository import PilotRepository

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pilot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(20),
            family_name VARCHAR(20)
        )
    """)
    yield conn
    conn.close()

@pytest.fixture
def pilot_repository(db_conn):
    return PilotRepository(db_conn)

@pytest.fixture
def sample_pilot():
    return Pilot(
        id=1,
        first_name="Andrea",
        family_name="Almond"
    )

class TestReadOperations:

    # READ methods
    def test_get_item_by_id_returns_pilot(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO pilot (first_name, family_name)
            VALUES ('Andrea', 'Almond')
        """)

        pilot = pilot_repository.get_item_by_id(1)

        assert pilot is not None
        assert pilot.id == 1

    def test_get_item_by_id_returns_none_when_missing(self, pilot_repository):
        assert pilot_repository.get_item_by_id(999) is None

class TestListOperations:

    def test_get_pilot_list_returns_sorted_list(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO pilot (first_name, family_name)
            VALUES
                ('Andrea', 'Almond'),
                ('Bertram', 'Bassett')
        """)

        pilot_list = pilot_repository.get_pilot_list()

        assert len(pilot_list) == 2
        assert pilot_list[0].family_name == "Almond"
        assert pilot_list[1].family_name == "Bassett"

    def test_get_pilot_list_returns_none_when_empty(self, pilot_repository):
        assert pilot_repository.get_pilot_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO pilot (first_name, family_name)
            VALUES
                ('Andrea', 'Almond'),
                ('Bertram', 'Almond')
        """)

        results = pilot_repository.search_on_field("family_name", "Almond")

        assert len(results) == 2
        assert all(a.family_name == "Almond" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, pilot_repository):
        assert pilot_repository.search_on_field("family_name", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, pilot_repository):
        with pytest.raises(Exception):
            pilot_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_item_persists_to_db(self, pilot_repository, db_conn, sample_pilot):
        pilot_repository.insert_item(sample_pilot)

        row = db_conn.execute(
            "SELECT * FROM pilot WHERE family_name = 'Almond'"
        ).fetchone()

        assert row is not None
        assert row["family_name"] == "Almond"

    def test_insert_item_prevents_duplicates(self, pilot_repository, db_conn, sample_pilot): # TODO - add better exception handling for any uniqueness constraints
        # No uniqueness or duplicate checking in the db table at present
        pass

    def test_update_item_updates_fields(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO pilot (first_name, family_name)
            VALUES ('Andrea', 'Almond')
        """)

        updated = Pilot(
            id=1,
            first_name="Anthea",
            family_name="Aspic"
        )
        pilot_repository.update_item(updated)

        row = db_conn.execute("SELECT * FROM pilot WHERE id = 1").fetchone()
        assert row["first_name"] == "Anthea"
        assert row["family_name"] == "Aspic"

    def test_update_item_prevents_duplicates(self, pilot_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
        # No uniqueness or duplicate checking in the db table at present
        pass

    def test_delete_item_removes_row(self, pilot_repository, db_conn, sample_pilot):
        db_conn.execute("""
            INSERT INTO pilot (first_name, family_name)
            VALUES ('Andrea', 'Almond')
        """)
        pilot_repository.delete_item(sample_pilot)

        row = db_conn.execute("SELECT * FROM pilot WHERE id = 1").fetchone()
        assert row is None

