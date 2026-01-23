import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.ui.airport_menu import AirportMenu
from flightmanagement.models.airport import Airport

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_bindings():
    return MagicMock()

@pytest.fixture
def mock_airport_service():
    service = MagicMock()
    service.get_airport_table.return_value = "AIRPORT TABLE"
    service.get_airport_choices.return_value = [(1, "AAA"), (2, "BBB")]
    service.get_airport_by_id.side_effect = lambda x: Airport(id=x, code="AAA")
    return service

@pytest.fixture
def menu(mock_session, mock_bindings, mock_airport_service):
    return AirportMenu(
        session=mock_session,
        bindings=mock_bindings,
        airport_service=mock_airport_service,
    )

class FakePrompt:
    def __init__(self, value=None, cancelled=False):
        self.value = value
        self.is_cancelled = cancelled

class TestLoad:

    def test_load_back_exits_menu(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.airport_menu.choice",
            return_value="back"
        )

        # Should simply exit without error
        menu.load()

    def test_load_show_calls_show_option(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.airport_menu.choice",
            side_effect=["show", "back"]
        )
        spy = mocker.spy(menu, "_AirportMenu__show_option")
        menu.load()

        spy.assert_called_once()

class TestShow:

    def test_show_option_prints_table(self, menu, mocker):
        menu._AirportMenu__airport_service.get_airport_table.return_value = "TABLE"
        mock_print = mocker.patch("builtins.print")
        menu._AirportMenu__show_option()

        mock_print.assert_any_call("TABLE")

class TestSearch:

    def test_search_option_cancelled(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.airport_menu.UserPrompt",
            return_value=FakePrompt(cancelled=True)
        )
        result = menu._AirportMenu__search_option()

        assert result is False

    def test_search_option_no_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.airport_menu.UserPrompt",
            return_value=FakePrompt("AAA")
        )
        menu._AirportMenu__airport_service.search_airport.return_value = []
        result = menu._AirportMenu__search_option()

        assert result is True

    def test_search_option_with_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.airport_menu.UserPrompt",
            return_value=FakePrompt("AAA")
        )

        airport = Airport(
            id=1,
            code="AAA",
            name="Test airport",
            city="Test city",
            country="Test country",
            region="Test region"
        )
        menu._AirportMenu__airport_service.search_airport.return_value = [airport]
        menu._AirportMenu__airport_service.get_results_view.return_value = "RESULTS"
        result = menu._AirportMenu__search_option()

        assert result is True

class TestAdd:

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_add_airport_cancelled(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._AirportMenu__add_option()

        assert result is False

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_add_airport_success(self, mock_prompt, menu, mock_airport_service):
        mock_prompt.side_effect = [
            FakePrompt("AAA"),              # code
            FakePrompt("Test airport"),     # name
            FakePrompt("Test city"),        # city
            FakePrompt("Test country"),     # country
            FakePrompt("Test region")       # region
        ]

        result = menu._AirportMenu__add_option()

        assert result is True
        mock_airport_service.add_airport.assert_called_once()

class TestUpdate:

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_update_cancelled_on_selection(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._AirportMenu__update_option()

        assert result is False

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_update_airport_success(self, mock_prompt, menu, mock_airport_service):
        # Existing airport returned from selection
        existing_airport = Airport(
            id=1,
            code="AAA",
            name="Test airport",
            city="Test city",
            country="Test country",
            region="Test region"
        )
        mock_airport_service.get_airport_by_id.return_value = existing_airport

        # Prompt sequence:
        # 1. Select airport ID
        # 2–8. Update prompts
        mock_prompt.side_effect = [
            FakePrompt(value=1),                # airport selection
            FakePrompt("BBB"),                  # code
            FakePrompt("Test airport 2"),       # name
            FakePrompt("Test city 2"),          # city
            FakePrompt("Test country 2"),       # country
            FakePrompt("Test region 2")         # region
        ]

        result = menu._AirportMenu__update_option()

        assert result is True
        mock_airport_service.update_airport.assert_called_once()

        updated_airport = mock_airport_service.update_airport.call_args[0][0]
        assert updated_airport.id == 1
        assert updated_airport.code == "AAA"

class TestDelete:

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_delete_airport_success(self, mock_prompt, menu, mock_airport_service):
        airport = Airport(id=1, code="AAA")
        mock_airport_service.get_airport_by_id.return_value = airport

        mock_prompt.side_effect = [
            FakePrompt(value=1),     # airport selection
            FakePrompt(value=True),  # confirm delete
        ]

        result = menu._AirportMenu__delete_option()

        assert result is True
        mock_airport_service.delete_airport.assert_called_once_with(airport)

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_delete_not_confirmed(self, mock_prompt, menu):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # airport choice
            FakePrompt(value=False) # confirmation
        ]

        result = menu._AirportMenu__delete_option()

        assert result is False

    @patch("flightmanagement.ui.airport_menu.UserPrompt")
    def test_delete_confirmed(self, mock_prompt, menu, mock_airport_service):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # airport choice
            FakePrompt(value=True),  # confirmation
        ]

        result = menu._AirportMenu__delete_option()

        assert result is True
        mock_airport_service.delete_airport.assert_called_once()

