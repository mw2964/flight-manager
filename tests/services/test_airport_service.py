import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.services.airport_service import AirportService
from flightmanagement.models.airport import Airport

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def service(mock_conn):
    mock_repo = MagicMock()
    return AirportService(mock_conn, airport_repository=mock_repo)

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

class TestAddData:

    @patch("flightmanagement.services.airport_service.transaction")
    def test_add_airport_inserts_airport(self, mock_transaction, service):
        airport = Airport(
            code="AAA",
            name="Andonovia International Airport",
            city="Andonovia",
            country="Bankantistan",
            region="Asia"
        )
        service.add_airport(airport)

        service._AirportService__airport_repository.insert_item.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.airport_service.transaction")
    def test_update_airport_updates_item(self, mock_transaction, service, sample_airport):
        service.update_airport(sample_airport)
        service._AirportService__airport_repository.update_item.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.airport_service.transaction")
    def test_delete_airport_deletes_item(self, mock_transaction, service, sample_airport):
        service.delete_airport(sample_airport)

        service._AirportService__airport_repository.delete_item.assert_called_once_with(sample_airport)

class TestUseRepository:

    def test_search_airport_calls_repository(self, service):
        service.search_airports("code", "AAA")

        service._AirportService__airport_repository.search_on_field.assert_called_once_with(
            "code", "AAA"
        )

    def test_get_airport_table_uses_repository(self, service, sample_airport):
        service._AirportService__airport_repository.get_airport_list.return_value = [
            sample_airport
        ]

        result = service.get_airport_table()

        assert "AAA" in result

class TestReturnData:

    def test_get_airport_by_id(self, service):
        service.get_airport_by_id(10)

        service._AirportService__airport_repository.get_item_by_id.assert_called_once_with(10)

    def test_get_airport_choices_returns_tuples(self, service, sample_airport):
        service._AirportService__airport_repository.get_airport_list.return_value = [
            sample_airport
        ]

        result = service.get_airport_choices()

        assert result == [
            (1, str(sample_airport))
        ]

    def test_get_airport_choices_empty_list(self, service):
        service._AirportService__airport_repository.get_airport_list.return_value = []

        result = service.get_airport_choices()

        assert result == []

    def test_get_results_view_empty_list(self, service):
        assert service.get_results_view([]) == ""

    def test_get_results_view_none(self, service):
        assert service.get_results_view(None) == ""

    def test_get_results_view_contains_airport_data(self, service, sample_airport):
        output = service.get_results_view([sample_airport])

        assert "AAA" in output
        assert "Andonovia" in output

