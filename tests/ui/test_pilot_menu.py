import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.ui.pilot_menu import PilotMenu
from flightmanagement.models.pilot import Pilot

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_bindings():
    return MagicMock()

@pytest.fixture
def mock_pilot_service():
    service = MagicMock()
    service.get_pilot_table.return_value = "PILOT TABLE"
    service.get_pilot_choices.return_value = [(1, "John Smith"), (2, "Sarah Jones")]
    service.get_pilot_by_id.side_effect = lambda x: Pilot(id=x, first_name="John", family_name="Smith")
    return service

@pytest.fixture
def menu(mock_session, mock_bindings, mock_pilot_service):
    return PilotMenu(
        session=mock_session,
        bindings=mock_bindings,
        pilot_service=mock_pilot_service,
    )

class FakePrompt:
    def __init__(self, value=None, cancelled=False):
        self.value = value
        self.is_cancelled = cancelled

class TestLoad:

    def test_load_back_exits_menu(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.pilot_menu.choice",
            return_value="back"
        )

        # Should simply exit without error
        menu.load()

    def test_load_show_calls_show_option(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.pilot_menu.choice",
            side_effect=["show", "back"]
        )
        spy = mocker.spy(menu, "_PilotMenu__show_option")
        menu.load()

        spy.assert_called_once()

class TestShow:

    def test_show_option_prints_table(self, menu, mocker):
        menu._PilotMenu__pilot_service.get_pilot_table.return_value = "TABLE"
        mock_print = mocker.patch("builtins.print")
        menu._PilotMenu__show_option()

        mock_print.assert_any_call("TABLE")

class TestSearch:

    def test_search_option_cancelled(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.pilot_menu.UserPrompt",
            return_value=FakePrompt(cancelled=True)
        )
        result = menu._PilotMenu__search_option()

        assert result is False

    def test_search_option_no_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.pilot_menu.UserPrompt",
            return_value=FakePrompt("Smith")
        )
        menu._PilotMenu__pilot_service.search_pilot.return_value = []
        result = menu._PilotMenu__search_option()

        assert result is True

    def test_search_option_with_results(self, menu, mocker):
        mocker.patch(
            "flightmanagement.ui.pilot_menu.UserPrompt",
            return_value=FakePrompt("Smith")
        )

        pilot = Pilot(
            id=1,
            first_name="John",
            family_name="Smith"
        )
        menu._PilotMenu__pilot_service.search_pilot.return_value = [pilot]
        menu._PilotMenu__pilot_service.get_results_view.return_value = "RESULTS"
        result = menu._PilotMenu__search_option()

        assert result is True

class TestAdd:

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_add_pilot_cancelled(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._PilotMenu__add_option()

        assert result is False

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_add_pilot_success(self, mock_prompt, menu, mock_pilot_service):
        mock_prompt.side_effect = [
            FakePrompt("John"),             # first_name
            FakePrompt("Smith"),            # family_name
        ]

        result = menu._PilotMenu__add_option()

        assert result is True
        mock_pilot_service.add_pilot.assert_called_once()

class TestUpdate:

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_update_cancelled_on_selection(self, mock_prompt, menu):
        mock_prompt.return_value = FakePrompt(cancelled=True)

        result = menu._PilotMenu__update_option()

        assert result is False

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_update_pilot_success(self, mock_prompt, menu, mock_pilot_service):
        # Existing pilot returned from selection
        existing_pilot = Pilot(
            id=1,
            first_name="John",
            family_name="Smith"
        )
        mock_pilot_service.get_pilot_by_id.return_value = existing_pilot

        # Prompt sequence:
        # 1. Select pilot ID
        # 2+. Update prompts
        mock_prompt.side_effect = [
            FakePrompt(value=1),    # pilot selection
            FakePrompt("Sarah"),    # first_name
            FakePrompt("Jones")     # family_name
        ]

        result = menu._PilotMenu__update_option()

        assert result is True
        mock_pilot_service.update_pilot.assert_called_once()

        updated_pilot = mock_pilot_service.update_pilot.call_args[0][0]
        assert updated_pilot.id == 1
        assert updated_pilot.first_name == "Sarah"

class TestDelete:

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_delete_pilot_success(self, mock_prompt, menu, mock_pilot_service):
        pilot = Pilot(id=1, first_name="John", family_name="Smith")
        mock_pilot_service.get_pilot_by_id.return_value = pilot

        mock_prompt.side_effect = [
            FakePrompt(value=1),     # pilot selection
            FakePrompt(value=True),  # confirm delete
        ]

        result = menu._PilotMenu__delete_option()

        assert result is True
        mock_pilot_service.delete_pilot.assert_called_once_with(pilot)

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_delete_not_confirmed(self, mock_prompt, menu):
        mock_prompt.side_effect = [
            FakePrompt(value=1),        # pilot choice
            FakePrompt(value=False)     # confirmation
        ]

        result = menu._PilotMenu__delete_option()

        assert result is False

    @patch("flightmanagement.ui.pilot_menu.UserPrompt")
    def test_delete_confirmed(self, mock_prompt, menu, mock_pilot_service):
        mock_prompt.side_effect = [
            FakePrompt(value=1),     # pilot choice
            FakePrompt(value=True),  # confirmation
        ]

        result = menu._PilotMenu__delete_option()

        assert result is True
        mock_pilot_service.delete_pilot.assert_called_once()

