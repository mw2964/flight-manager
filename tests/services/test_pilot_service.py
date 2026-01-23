import pytest
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
        id=1,
        first_name="Andrea",
        family_name="Almond"
    )

class TestAddData:

    @patch("flightmanagement.services.pilot_service.transaction")
    def test_add_pilot_inserts_pilot(self, mock_transaction, service):
        pilot = Pilot(
            first_name="Andrea",
            family_name="Almond"
        )
        service.add_pilot(pilot)

        service._PilotService__pilot_repository.insert_item.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.pilot_service.transaction")
    def test_update_pilot_updates_item(self, mock_transaction, service, sample_pilot):
        service.update_pilot(sample_pilot)

        service._PilotService__pilot_repository.update_item.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.pilot_service.transaction")
    def test_delete_pilot_deletes_item(self, mock_transaction, service, sample_pilot):
        service.delete_pilot(sample_pilot)

        service._PilotService__pilot_repository.delete_item.assert_called_once_with(sample_pilot)

class TestUseRepository:

    def test_search_pilot_calls_repository(self, service):
        service.search_pilots("family_name", "Almond")

        service._PilotService__pilot_repository.search_on_field.assert_called_once_with(
            "family_name", "Almond"
        )

    def test_get_pilot_table_uses_repository(self, service, sample_pilot):
        service._PilotService__pilot_repository.get_pilot_list.return_value = [
            sample_pilot
        ]

        result = service.get_pilot_table()

        assert "Almond" in result

class TestReturnData:

    def test_get_pilot_by_id(self, service):
        service.get_pilot_by_id(10)

        service._PilotService__pilot_repository.get_item_by_id.assert_called_once_with(10)

    def test_get_pilot_choices_returns_tuples(self, service, sample_pilot):
        service._PilotService__pilot_repository.get_pilot_list.return_value = [
            sample_pilot
        ]

        result = service.get_pilot_choices()

        assert result == [
            (1, str(sample_pilot))
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

        assert "Andrea" in output
        assert "Almond" in output

