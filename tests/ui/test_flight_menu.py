import pytest
from unittest.mock import MagicMock, patch
from datetime import date, time
from flightmanagement.ui.flight_menu import FlightMenu, FlightUpdateMenu
from flightmanagement.models.flight import Flight
from flightmanagement.error import UserCancelled
from flightmanagement.services.flight_service import DependentRecords

@pytest.fixture
def flight_service():
    return MagicMock()

@pytest.fixture
def menu(flight_service):
    session = MagicMock()
    bindings = MagicMock()
    return FlightMenu(
        session=session,
        bindings=bindings,
        conn=None,
        flight_service=flight_service,
    )

@pytest.fixture
def flight():
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

class TestLoad:

    @patch("flightmanagement.ui.flight_menu.choice")
    def test_load_exits_on_back(self, mock_choice, menu):
        mock_choice.return_value = "back"

        menu.load()  # should exit cleanly

class TestAdd:

    def test_add_flight_success(self, menu, flight_service, capsys):
        new_flight = MagicMock()
        menu._prompt_add_flight = MagicMock(return_value=new_flight)
        flight_service.add_flight.return_value = 42

        menu._add_option()

        flight_service.add_flight.assert_called_once_with(new_flight)
        out = capsys.readouterr().out
        assert "successfully added" in out

class TestGetFlightFromSelection:

    def test_get_flight_from_selection(self, menu, flight_service, flight):
        menu._prompt_until_valid = MagicMock(return_value=1)
        flight_service.get_flight_by_id.return_value = flight

        result = menu._get_flight_from_selection()

        assert result is flight
        flight_service.get_flight_by_id.assert_called_once_with(1)

    def test_get_flight_missing_id_raises(self, menu, flight_service):
        bad_flight = MagicMock(flight_id=None)
        menu._prompt_until_valid = MagicMock(return_value=1)
        flight_service.get_flight_by_id.return_value = bad_flight

        with pytest.raises(ValueError):
            menu._get_flight_from_selection()
