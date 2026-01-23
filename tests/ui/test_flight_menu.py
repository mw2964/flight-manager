import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from flightmanagement.ui.flight_menu import FlightMenu
from flightmanagement.models.flight import Flight

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_bindings():
    return MagicMock()

@pytest.fixture
def mock_flight_service():
    service = MagicMock()
    service.get_flight_table.return_value = "FLIGHT TABLE"
    service.get_flight_choices.return_value = [(1, "ZMY123"), (2, "ZMY234")]
    service.get_flight_by_id.side_effect = lambda x: Flight(id=x, flight_number="ZMY123", aircraft_id=1, origin_id=1, destination_id=2, departure_time_scheduled=datetime(2026, 1, 1, 15, 30))
    return service

@pytest.fixture
def mock_aircraft_service():
    service = MagicMock()
    service.get_aircraft_choices.return_value = [(1, "G-TEST1"), (2, "G-TEST2")]
    return service

@pytest.fixture
def mock_airport_service():
    service = MagicMock()
    service.get_airport_choices.return_value = [(1, "AAA"), (2, "BBB")]
    return service

@pytest.fixture
def mock_pilot_service():
    service = MagicMock()
    service.get_pilot_choices.return_value = [(1, "John Smith"), (2, "Sarah Jones")]
    return service
    
@pytest.fixture
def menu(mock_session, mock_bindings, mock_flight_service, mock_aircraft_service, mock_airport_service, mock_pilot_service):
    return FlightMenu(
        session=mock_session,
        bindings=mock_bindings,
        flight_service=mock_flight_service,
        aircraft_service=mock_aircraft_service,
        airport_service=mock_airport_service,
        pilot_service=mock_pilot_service
    )

class FakePrompt:
    def __init__(self, value=None, cancelled=False):
        self.value = value
        self.is_cancelled = cancelled
    
    def run(self):
        return self.value

class TestLoad:

    def test_load_back_exits_menu(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.flight_menu.choice",
            return_value="back"
        )

        # Should simply exit without error
        menu.load()

    def test_load_show_calls_show_option(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.flight_menu.choice",
            side_effect=["show", "back"]
        )
        spy = mocker.spy(menu, "_FlightMenu__show_option")
        menu.load()

        spy.assert_called_once()

class TestShow:

    def test_show_option_prints_table(self, menu, mocker):
        menu._FlightMenu__flight_service.get_flight_table.return_value = "TABLE"
        mock_print = mocker.patch("builtins.print")
        menu._FlightMenu__show_option()

        mock_print.assert_any_call("TABLE")

class TestSearch:

    def test_search_option_cancelled(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.flight_menu.UserPrompt",
            return_value=FakePrompt(cancelled=True)
        )
        result = menu._FlightMenu__search_option()

        assert result is False

    def test_search_option_no_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.flight_menu.UserPrompt",
            return_value=FakePrompt("G-TEST")
        )
        menu._FlightMenu__flight_service.search_flight.return_value = []
        result = menu._FlightMenu__search_option()

        assert result is True

    def test_search_option_with_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.flight_menu.UserPrompt",
            return_value=FakePrompt("ZMY123")
        )

        flight = Flight(
            id=1,
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 1, 15, 30)
        )
        menu._FlightMenu__flight_service.search_flight.return_value = [flight]
        menu._FlightMenu__flight_service.get_results_view.return_value = "RESULTS"
        result = menu._FlightMenu__search_option()

        assert result is True

class TestAdd:

    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_add_flight_cancelled(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._FlightMenu__add_option()

        assert result is False

    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_add_flight_success(self, mock_prompt, menu, mock_flight_service):
        mock_prompt.side_effect = [
            FakePrompt("ZMY123"),       # flight_number
            FakePrompt(1),              # aircraft_id
            FakePrompt(1),              # origin_id
            FakePrompt(2),              # destination_id
            FakePrompt(1),              # pilot_id
            FakePrompt(2),              # copilot_id
            FakePrompt("2026-01-01"),   # departure_date_scheduled
            FakePrompt("15:30"),        # departure_time_scheduled
            FakePrompt("2026-01-01"),   # arrival_date_scheduled
            FakePrompt("16:55")         # arrival_time_scheduled
        ]

        result = menu._FlightMenu__add_option()

        assert result is True
        mock_flight_service.add_flight.assert_called_once()


class TestUpdate:

    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_update_cancelled_on_selection(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._FlightMenu__update_option()

        assert result is False


    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_update_flight_success(self, mock_prompt, menu, mock_flight_service):
        # Existing flight returned from selection
        existing_flight = Flight(
            id=1,
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 1, 15, 30)
        )
        mock_flight_service.get_flight_by_id.return_value = existing_flight

        # Prompt sequence:
        # 1. Select flight ID
        # 2+. Update prompts
        mock_prompt.side_effect = [
            FakePrompt(value=1),        # flight selection
            FakePrompt("ZMY123"),       # flight_number
            FakePrompt(1),              # aircraft_id
            FakePrompt(1),              # origin_id
            FakePrompt(2),              # destination_id
            FakePrompt(1),              # pilot_id
            FakePrompt(2),              # copilot_id
            FakePrompt("2026-01-01"),   # departure_date_scheduled
            FakePrompt("15:30"),        # departure_time_scheduled
            FakePrompt("2026-01-01"),   # arrival_date_scheduled
            FakePrompt("16:55"),        # arrival_time_scheduled
            FakePrompt("2026-01-01"),   # departure_date_actual
            FakePrompt("15:35"),        # departure_time_actual
            FakePrompt("2026-01-01"),   # arrival_date_actual
            FakePrompt("16:50"),        # arrival_time_actual
            FakePrompt("Scheduled")     # status
        ]

        result = menu._FlightMenu__update_option()

        assert result is True
        mock_flight_service.update_flight.assert_called_once()

        updated_flight = mock_flight_service.update_flight.call_args[0][0]
        assert updated_flight.id == 1
        assert updated_flight.flight_number == "ZMY123"

class TestDelete:

    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_delete_flight_success(self, mock_prompt, menu, mock_flight_service):
        flight = Flight(
            id=1,
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 1, 15, 30)
        )
        mock_flight_service.get_flight_by_id.return_value = flight

        mock_prompt.side_effect = [
            FakePrompt(value=1),     # flight selection
            FakePrompt(value=True),  # confirm delete
        ]

        result = menu._FlightMenu__delete_option()

        assert result is True
        mock_flight_service.delete_flight.assert_called_once_with(flight)

    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_delete_not_confirmed(self, mock_prompt, menu):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # flight choice
            FakePrompt(value=False) # confirmation
        ]

        result = menu._FlightMenu__delete_option()

        assert result is False

    @patch("flightmanagement.ui.flight_menu.UserPrompt")
    def test_delete_confirmed(self, mock_prompt, menu, mock_flight_service):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # flight choice
            FakePrompt(value=True),  # confirmation
        ]

        result = menu._FlightMenu__delete_option()

        assert result is True
        mock_flight_service.delete_flight.assert_called_once()

