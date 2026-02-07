import pytest
from unittest.mock import MagicMock, patch
from datetime import date, time

from flightmanagement.services.flight_service import FlightService
from flightmanagement.services.location_service import LocationService
from flightmanagement.models.flight import Flight
from flightmanagement.models.location import Location

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def flightservice(mock_conn):
    mock_repo = MagicMock()
    return FlightService(mock_conn, flight_repository=mock_repo)

@pytest.fixture
def locationservice(mock_conn):
    mock_repo = MagicMock()
    return LocationService(mock_conn, location_repository=mock_repo)

@pytest.fixture
def sample_flight():
    return Flight(
        flight_id=1,
        flight_number="ZMY123",
        aircraft_id=1,
        origin_location_id=1,
        departure_gate_id=1,
        destination_location_id=2,
        arrival_gate_id=2,
        captain_id=1,
        first_officer_id=2,
        scheduled_departure_date=date(2026, 1, 1),
        scheduled_departure_time=time(15, 30),
        scheduled_arrival_date=date(2026, 1, 1),
        scheduled_arrival_time=time(16, 55),
        confirmed_departure_date=date(2026, 1, 2),
        confirmed_departure_time=time(15, 30),
        confirmed_arrival_date=date(2026, 1, 2),
        confirmed_arrival_time=time(16, 50),
        flight_status="Arrived"
    )

@pytest.fixture
def sample_origin():
    return Location(
        location_id=1,
        location_type="Airport",
        iata_airport_code="ABC",
        location_name="Test Airport",
        town_or_city="Milton Keynes",
        country="United Kingdom",
    )

@pytest.fixture
def sample_destination():
    return Location(
        location_id=2,
        location_type="Airport",
        iata_airport_code="XYZ",
        location_name="Test Airport 2",
        town_or_city="Milton Keynes",
        country="United Kingdom",
    )


class TestAddData:

    @patch("flightmanagement.services.flight_service.transaction")
    def test_add_flight_inserts_flight(self, mock_transaction, flightservice):
        flight = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_location_id=1,
            departure_gate_id=1,
            destination_location_id=2,
            arrival_gate_id=2,
            captain_id=1,
            first_officer_id=2,
            scheduled_departure_date=date(2026, 1, 1),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 1),
            scheduled_arrival_time=time(16, 55),
            confirmed_departure_date=date(2026, 1, 2),
            confirmed_departure_time=time(15, 30),
            confirmed_arrival_date=date(2026, 1, 2),
            confirmed_arrival_time=time(16, 50),
            flight_status="Arrived"
        )
        flightservice.add_flight(flight)

        flightservice._FlightService__flight_repository.insert_flight.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.flight_service.transaction")
    def test_update_flight_updates_item(self, mock_transaction, flightservice, sample_flight):
        flightservice.update_flight(sample_flight)
        flightservice._FlightService__flight_repository.update_flight.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.flight_service.transaction")
    def test_delete_flight_deletes_item(self, mock_transaction, flightservice, sample_flight):
        flightservice.delete_flight(sample_flight)

        flightservice._FlightService__flight_repository.delete_flight.assert_called_once_with(sample_flight)

class TestUseRepository:

    def test_search_flight_calls_repository(self, flightservice):
        flightservice.search_flights("flight_number", "ZMY123")

        flightservice._FlightService__flight_repository.search_on_field.assert_called_once_with(
            "flight_number", "ZMY123"
        )

    def test_get_flight_table_uses_repository(self, flightservice, sample_flight):
        flightservice._FlightService__flight_repository.get_flight_list.return_value = [
            sample_flight
        ]

        result = flightservice.get_flight_table()

        assert "ZMY123" in result

class TestReturnData:

    def test_get_flight_by_id(self, flightservice):
        flightservice.get_flight_by_id(10)

        flightservice._FlightService__flight_repository.get_flight_by_id.assert_called_once_with(10)

    def test_get_flight_choices_returns_tuples(self, flightservice, locationservice, sample_flight, sample_origin, sample_destination):

        flightservice._FlightService__flight_repository.get_flight_list.return_value = [
            sample_flight
        ]

        result = flightservice.get_flight_choices()

        expected_summary = flightservice.get_flight_summary(sample_flight)

        assert result == [
            (sample_flight.flight_id, expected_summary)
        ]

    def test_get_flight_choices_empty_list(self, flightservice):
        flightservice._FlightService__flight_repository.get_flight_list.return_value = []

        result = flightservice.get_flight_choices()

        assert result == []

    def test_get_results_view_empty_list(self, flightservice):
        assert flightservice.get_results_view([]) == ""

    def test_get_results_view_none(self, flightservice):
        assert flightservice.get_results_view(None) == ""

    def test_get_results_view_contains_flight_data(self, flightservice, sample_flight):
        output = flightservice.get_results_view([sample_flight])

        assert "ZMY123" in output
        assert "2026-01-01 16:55" in output

