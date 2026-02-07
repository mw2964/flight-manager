import pytest
from datetime import date
from unittest.mock import MagicMock, patch
from flightmanagement.services.pilot_service import PilotService
from flightmanagement.models.pilot import Pilot

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def service(mock_conn):
    mock_repo = MagicMock()
    return PilotService(mock_conn, pilot_repository=mock_repo)

@pytest.fixture
def sample_pilot():
    return Pilot(
        staff_id=1,
        employee_number="E0001",
        first_name="Jane",
        family_name="Goodall",
        employment_start_date=date(2025, 1, 15),
        employment_end_date=date(2026, 2, 22),
        employment_status="Current",
        license_number="TEST001",
        license_type="TVL",
        license_expiration_date=date(2029, 12, 31)
    )

class TestAddData:

    @patch("flightmanagement.services.pilot_service.transaction")
    def test_add_pilot_inserts_pilot(self, mock_transaction, service):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_end_date=date(2026, 2, 22),
            employment_status="Current",
            license_number="TEST001",
            license_type="TVL",
            license_expiration_date=date(2029, 12, 31)
        )
        service.add_pilot(pilot)

        service._PilotService__pilot_repository.insert_pilot.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.pilot_service.transaction")
    def test_update_pilot_updates_item(self, mock_transaction, service, sample_pilot):
        service.update_pilot(sample_pilot)

        service._PilotService__pilot_repository.update_pilot.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.pilot_service.transaction")
    def test_delete_pilot_deletes_item(self, mock_transaction, service, sample_pilot):
        service.delete_pilot(sample_pilot)

        service._PilotService__pilot_repository.delete_pilot.assert_called_once_with(sample_pilot)

class TestUseRepository:

    def test_search_pilot_calls_repository(self, service):
        service.search_pilots("family_name", "Goodall")

        service._PilotService__pilot_repository.search_on_field.assert_called_once_with(
            "family_name", "Goodall"
        )

    def test_get_pilot_table_uses_repository(self, service, sample_pilot):
        service._PilotService__pilot_repository.get_pilot_list.return_value = [
            sample_pilot
        ]

        result = service.get_pilot_table()

        assert "Goodall" in result

class TestReturnData:

    def test_get_pilot_by_id(self, service):
        service.get_pilot_by_id(10)

        service._PilotService__pilot_repository.get_pilot_by_id.assert_called_once_with(10)

    def test_get_pilot_choices_returns_tuples(self, service, sample_pilot):
        service._PilotService__pilot_repository.get_pilot_list.return_value = [
            sample_pilot
        ]

        result = service.get_pilot_choices()

        assert result == [
            (1, f"{sample_pilot.family_name}, {sample_pilot.first_name}")
        ]

    def test_get_pilot_choices_empty_list(self, service):
        service._PilotService__pilot_repository.get_pilot_list.return_value = []

        result = service.get_pilot_choices()

        assert result == []

    def test_get_results_view_empty_list(self, service):
        assert service.get_results_view([]) == ""

    def test_get_results_view_none(self, service):
        assert service.get_results_view(None) == ""

    def test_get_results_view_contains_pilot_data(self, service, sample_pilot):
        output = service.get_results_view([sample_pilot])

        assert "Jane" in output
        assert "Goodall" in output

