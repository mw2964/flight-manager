import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.ui.aircraft_menu import AircraftMenu
from flightmanagement.models.aircraft import Aircraft

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_bindings():
    return MagicMock()

@pytest.fixture
def mock_aircraft_service():
    service = MagicMock()
    service.get_aircraft_table.return_value = "AIRCRAFT TABLE"
    service.get_aircraft_choices.return_value = [(1, "G-ABCD"), (2, "G-BCDE")]
    service.get_aircraft_by_id.side_effect = lambda x: Aircraft(id=x, registration="N123", manufacturer="Boeing", model="747")
    return service

@pytest.fixture
def menu(mock_session, mock_bindings, mock_aircraft_service):
    return AircraftMenu(
        session=mock_session,
        bindings=mock_bindings,
        aircraft_service=mock_aircraft_service,
    )

class FakePrompt:
    def __init__(self, value=None, cancelled=False):
        self.value = value
        self.is_cancelled = cancelled

class TestLoad:

    def test_load_back_exits_menu(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.aircraft_menu.choice",
            return_value="back"
        )

        # Should simply exit without error
        menu.load()

    def test_load_show_calls_show_option(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.aircraft_menu.choice",
            side_effect=["show", "back"]
        )
        spy = mocker.spy(menu, "_AircraftMenu__show_option")
        menu.load()

        spy.assert_called_once()

class TestShow:

    def test_show_option_prints_table(self, menu, mocker):
        menu._AircraftMenu__aircraft_service.get_aircraft_table.return_value = "TABLE"
        mock_print = mocker.patch("builtins.print")
        menu._AircraftMenu__show_option()

        mock_print.assert_any_call("TABLE")

class TestSearch:

    def test_search_option_cancelled(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.aircraft_menu.UserPrompt",
            return_value=FakePrompt(cancelled=True)
        )
        result = menu._AircraftMenu__search_option()

        assert result is False

    def test_search_option_no_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.aircraft_menu.UserPrompt",
            return_value=FakePrompt("G-TEST")
        )
        menu._AircraftMenu__aircraft_service.search_aircraft.return_value = []
        result = menu._AircraftMenu__search_option()

        assert result is True

    def test_search_option_with_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.aircraft_menu.UserPrompt",
            return_value=FakePrompt("G-TEST")
        )

        aircraft = Aircraft(
            id=1,
            registration="G-TEST",
            manufacturer_serial_no=1,
            icao_hex="ABC",
            manufacturer="Boeing",
            model="737",
            icao_type="B737",
            status="Active"
        )
        menu._AircraftMenu__aircraft_service.search_aircraft.return_value = [aircraft]
        menu._AircraftMenu__aircraft_service.get_results_view.return_value = "RESULTS"
        result = menu._AircraftMenu__search_option()

        assert result is True

class TestAdd:

    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_add_aircraft_cancelled(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._AircraftMenu__add_option()

        assert result is False

    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_add_aircraft_success(self, mock_prompt, menu, mock_aircraft_service):
        mock_prompt.side_effect = [
            FakePrompt("N123"),      # registration
            FakePrompt(100),         # serial
            FakePrompt("ABC123"),    # icao_hex
            FakePrompt("Airbus"),    # manufacturer
            FakePrompt("A320"),      # model
            FakePrompt("A320"),      # icao_type
            FakePrompt("Active"),    # status
        ]

        result = menu._AircraftMenu__add_option()

        assert result is True
        mock_aircraft_service.add_aircraft.assert_called_once()


class TestUpdate:

    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_update_cancelled_on_selection(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._AircraftMenu__update_option()

        assert result is False


    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_update_aircraft_success(self, mock_prompt, menu, mock_aircraft_service):
        # Existing aircraft returned from selection
        existing_aircraft = Aircraft(
            id=1,
            registration="N123",
            manufacturer_serial_no=100,
            icao_hex="ABC123",
            manufacturer="Airbus",
            model="A320",
            icao_type="A320",
            status="Active",
        )
        mock_aircraft_service.get_aircraft_by_id.return_value = existing_aircraft

        # Prompt sequence:
        # 1. Select aircraft ID
        # 2–8. Update prompts
        mock_prompt.side_effect = [
            FakePrompt(value=1),            # aircraft selection
            FakePrompt("N124"),              # registration
            FakePrompt(101),                 # serial
            FakePrompt("DEF456"),             # icao_hex
            FakePrompt("Airbus"),             # manufacturer
            FakePrompt("A321"),               # model
            FakePrompt("A321"),               # icao_type
            FakePrompt("Inactive"),           # status
        ]

        result = menu._AircraftMenu__update_option()

        assert result is True
        mock_aircraft_service.update_aircraft.assert_called_once()

        updated_aircraft = mock_aircraft_service.update_aircraft.call_args[0][0]
        assert updated_aircraft.id == 1
        assert updated_aircraft.registration == "N124"
        assert updated_aircraft.status == "Inactive"

class TestDelete:

    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_delete_aircraft_success(self, mock_prompt, menu, mock_aircraft_service):
        aircraft = Aircraft(id=1, registration="N123", manufacturer="Boeing", model="747")
        mock_aircraft_service.get_aircraft_by_id.return_value = aircraft

        mock_prompt.side_effect = [
            FakePrompt(value=1),     # aircraft selection
            FakePrompt(value=True),  # confirm delete
        ]

        result = menu._AircraftMenu__delete_option()

        assert result is True
        mock_aircraft_service.delete_aircraft.assert_called_once_with(aircraft)

    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_delete_not_confirmed(self, mock_prompt, menu):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # aircraft choice
            FakePrompt(value=False) # confirmation
        ]

        result = menu._AircraftMenu__delete_option()

        assert result is False

    @patch("flightmanagement.ui.aircraft_menu.UserPrompt")
    def test_delete_confirmed(self, mock_prompt, menu, mock_aircraft_service):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # aircraft choice
            FakePrompt(value=True),  # confirmation
        ]

        result = menu._AircraftMenu__delete_option()

        assert result is True
        mock_aircraft_service.delete_aircraft.assert_called_once()

