import sqlite3
import pytest
from datetime import date
from flightmanagement.error import UniqueConstraintViolation, ForeignKeyDependencyViolation
from flightmanagement.models.pilot import Pilot
from flightmanagement.repositories.pilot_repository import PilotRepository
from flightmanagement.db.db import initialise_schema

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    initialise_schema(conn)
    yield conn
    conn.close()

@pytest.fixture
def pilot_repository(db_conn):
    return PilotRepository(db_conn)

@pytest.fixture
def sample_pilot():
    return Pilot(
        staff_member_id=1,
        employee_number="E0001",
        first_name="Jane",
        family_name="Goodall",
        employment_start_date=date(2025, 1, 15),
        employment_end_date=None,
        employment_status="Current",
        license_number="TEST001",
        license_type="TVL",
        license_expiration_date=date(2029, 12, 31)
    )

class TestReadOperations:

    # READ methods
    def test_get_pilot_by_id_returns_pilot(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Morrison', 'Current', '2014-04-13', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15')
        """)

        pilot = pilot_repository.get_pilot_by_id(1)

        assert pilot is not None
        assert pilot.staff_member_id == 1

    def test_get_pilot_by_id_returns_none_when_missing(self, pilot_repository):
        assert pilot_repository.get_pilot_by_id(999) is None

class TestListOperations:

    def test_get_pilot_list_returns_sorted_list(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Morrison', 'Current', '2014-04-13', NULL),
                ('FC002', 'Emily', 'Carter', 'Current', '2021-10-23', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15'),
                (2, 'AVLC-09436', 'ATPL', '2034-10-30')
        """)

        pilot_list = pilot_repository.get_pilot_list()

        assert len(pilot_list) == 2
        assert pilot_list[0].family_name == "Carter"
        assert pilot_list[1].family_name == "Morrison"

    def test_get_pilot_list_returns_none_when_empty(self, pilot_repository):
        assert pilot_repository.get_pilot_list() == []

class TestSearchOperations:

    def test_search_on_field_returns_matches(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Carter', 'Current', '2014-04-13', NULL),
                ('FC002', 'Emily', 'Carter', 'Current', '2021-10-23', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15'),
                (2, 'AVLC-09436', 'ATPL', '2034-10-30')
        """)

        results = pilot_repository.search_on_field("family_name", "Carter")

        assert len(results) == 2
        assert all(a.family_name == "Carter" for a in results)

    def test_search_on_field_returns_none_when_no_matches(self, pilot_repository):
        assert pilot_repository.search_on_field("family_name", "Unknown") == []

    def test_search_on_field_invalid_column_raises_error(self, pilot_repository):
        with pytest.raises(Exception):
            pilot_repository.search_on_field("invalid_column", "value")

class TestWriteOperations:

    def test_insert_pilot_persists_to_db(self, pilot_repository, db_conn, sample_pilot):
        pilot_repository.insert_pilot(sample_pilot)

        row = db_conn.execute(
            "SELECT * FROM vw_staff_pilots WHERE family_name = 'Goodall'"
        ).fetchone()

        assert row is not None
        assert row["family_name"] == "Goodall"

    def test_insert_pilot_prevents_duplicates(self, pilot_repository, db_conn, sample_pilot):
        pilot_repository.insert_pilot(sample_pilot)

        with pytest.raises(UniqueConstraintViolation):
            pilot_repository.insert_pilot(sample_pilot)

    def test_update_pilot_updates_fields(self, pilot_repository, db_conn):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Carter', 'Current', '2014-04-13', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15')
        """)

        updated = Pilot(
            staff_member_id=1,
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_end_date=date(2026, 2, 22),
            employment_status="Left",
            license_number="TEST001",
            license_type="TVL",
            license_expiration_date=date(2029, 12, 31)
        )
        pilot_repository.update_pilot(updated)

        row = db_conn.execute("SELECT * FROM vw_staff_pilots WHERE staff_member_id = 1").fetchone()
        assert row["employee_number"] == "E0001"
        assert row["first_name"] == "Jane"
        assert row["family_name"] == "Goodall"
        assert row["employment_start_date"] == "2025-01-15"
        assert row["employment_end_date"] == "2026-02-22"
        assert row["employment_status"] == "Left"
        assert row["license_number"] == "TEST001"
        assert row["license_type"] == "TVL"
        assert row["license_expiration_date"] == "2029-12-31"

    def test_update_pilot_prevents_duplicates(self, pilot_repository, db_conn): # TODO - add better exception handling for any uniqueness constraints
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Carter', 'Current', '2014-04-13', NULL),
                ('FC002', 'Emily', 'Carter', 'Current', '2021-10-23', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15'),
                (2, 'AVLC-09436', 'ATPL', '2034-10-30')
        """)

        updated = Pilot(
            staff_member_id=1,
            employee_number="FC002",
            first_name="Alex",
            family_name="Carter",
            employment_start_date=date(2014, 4, 13),
            employment_end_date=date(2026, 2, 22),
            employment_status="Left",
            license_number="AVLC-09435",
            license_type="ATPL",
            license_expiration_date=date(2034, 10, 30)
        )

        with pytest.raises(UniqueConstraintViolation):
            pilot_repository.update_pilot(updated)

    def test_delete_pilot_removes_row(self, pilot_repository, db_conn, sample_pilot):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Carter', 'Current', '2014-04-13', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15')
        """)

        pilot_repository.delete_pilot(sample_pilot)

        pilot_row = db_conn.execute("SELECT * FROM pilots WHERE staff_member_id = 1").fetchone()
        
        assert pilot_row is None

    def test_delete_staff_with_pilot_raises_key_violation(self, pilot_repository, db_conn, sample_pilot):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Carter', 'Current', '2014-04-13', NULL)
        """)

        db_conn.execute("""
            INSERT INTO pilots (staff_member_id, license_number, license_type, license_expiration_date)
            VALUES
                (1, 'AVLC-09435', 'ATPL', '2029-07-15')
        """)

        with pytest.raises(ForeignKeyDependencyViolation):
            pilot_repository.delete_staff_member(sample_pilot)

    def test_delete_staff_removes_row(self, pilot_repository, db_conn, sample_pilot):
        db_conn.execute("""
            INSERT INTO staff_members (employee_number, first_name, family_name, employment_status, employment_start_date, employment_end_date)
            VALUES
                ('FC001', 'Alex', 'Carter', 'Current', '2014-04-13', NULL)
        """)

        pilot_repository.delete_staff_member(sample_pilot)
        staff_row = db_conn.execute("SELECT * FROM staff_members WHERE staff_member_id = 1").fetchone()
        
        assert staff_row is None

