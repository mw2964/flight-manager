import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from flightmanagement.services.flight_service import FlightService
from flightmanagement.models.flight import Flight

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def service(mock_conn):
    mock_repo = MagicMock()
    return FlightService(mock_conn, flight_repository=mock_repo)

@pytest.fixture
def sample_flight():
    return Flight(
        id=1,
        flight_number="ZMY123",
        aircraft_id=1,
        origin_id=1,
        destination_id=2,
        pilot_id=1,
        copilot_id=2,
        departure_time_scheduled=datetime(2026, 1, 1, 15, 30),
        arrival_time_scheduled=datetime(2026, 1, 1, 16, 55),
        departure_time_actual=datetime(2026, 1, 2, 15, 30),
        arrival_time_actual=datetime(2026, 1, 2, 16, 50),
        status="Arrived"
    )

class TestAddData:

    @patch("flightmanagement.services.flight_service.transaction")
    def test_add_flight_inserts_flight(self, mock_transaction, service):
        flight = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            pilot_id=1,
            copilot_id=2,
            departure_time_scheduled=datetime(2026, 1, 1, 15, 30),
            arrival_time_scheduled=datetime(2026, 1, 1, 16, 55)
        )
        service.add_flight(flight)

        service._FlightService__flight_repository.insert_item.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.flight_service.transaction")
    def test_update_flight_updates_item(self, mock_transaction, service, sample_flight):
        service.update_flight(sample_flight)
        service._FlightService__flight_repository.update_item.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.flight_service.transaction")
    def test_delete_flight_deletes_item(self, mock_transaction, service, sample_flight):
        service.delete_flight(sample_flight)

        service._FlightService__flight_repository.delete_item.assert_called_once_with(sample_flight)

class TestUseRepository:

    def test_search_flight_calls_repository(self, service):
        service.search_flights("flight_number", "ZMY123")

        service._FlightService__flight_repository.search_on_field.assert_called_once_with(
            "flight_number", "ZMY123"
        )

    def test_get_flight_table_uses_repository(self, service, sample_flight):
        service._FlightService__flight_repository.get_flight_list.return_value = [
            sample_flight
        ]

        result = service.get_flight_table()

        assert "ZMY123" in result

class TestReturnData:

    def test_get_flight_by_id(self, service):
        service.get_flight_by_id(10)

        service._FlightService__flight_repository.get_item_by_id.assert_called_once_with(10)

    def test_get_flight_choices_returns_tuples(self, service, sample_flight):
        pass # TODO

    def test_get_flight_choices_empty_list(self, service):
        service._FlightService__flight_repository.get_flight_list.return_value = []

        result = service.get_flight_choices()

        assert result == []

    def test_get_results_view_empty_list(self, service):
        assert service.get_results_view([]) == ""

    def test_get_results_view_none(self, service):
        assert service.get_results_view(None) == ""

    def test_get_results_view_contains_flight_data(self, service, sample_flight):
        output = service.get_results_view([sample_flight])

        assert "ZMY123" in output
        assert "2026-01-01 16:55" in output

