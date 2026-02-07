import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.ui.aircraft_menu import AircraftMenu
from flightmanagement.models.aircraft import Aircraft
from flightmanagement.error import UserCancelled
from flightmanagement.services.aircraft_service import ConstraintViolation

@pytest.fixture
def aircraft_service():
    return MagicMock()

@pytest.fixture
def menu(aircraft_service):
    session = MagicMock()
    bindings = MagicMock()
    return AircraftMenu(
        session=session,
        bindings=bindings,
        conn=None,
        aircraft_service=aircraft_service,
    )

@pytest.fixture
def aircraft():
    return Aircraft(
        aircraft_id=1,
        aircraft_type_id=10,
        registration="G-TEST",
        manufacturer_serial_no=1234,
        icao_hex="ABC123",
        aircraft_status="Active",
    )

class TestLoad:

    @patch("flightmanagement.ui.aircraft_menu.choice")
    def test_load_routes_to_show(self, mock_choice, menu):
        mock_choice.side_effect = ["show", "back"]
        menu._show_option = MagicMock()

        menu.load()

        menu._show_option.assert_called_once()

    @patch("flightmanagement.ui.aircraft_menu.choice")
    def test_load_handles_user_cancelled(self, mock_choice, menu):
        mock_choice.side_effect = ["show", "back"]
        menu._show_option = MagicMock(side_effect=UserCancelled("cancel"))

        menu.load()

        menu._show_option.assert_called_once()

    @patch("flightmanagement.ui.aircraft_menu.choice")
    def test_load_exits_on_back(self, mock_choice, menu):
        mock_choice.return_value = "back"

        menu.load()  # should exit cleanly


class TestShow:

    def test_show_prints_aircraft_table(self, menu, aircraft_service, capsys):
        aircraft_service.get_aircraft_table.return_value = "AIRCRAFT TABLE"

        menu._show_option()

        out = capsys.readouterr().out
        assert "Displaying all aircraft" in out
        assert "AIRCRAFT TABLE" in out

class TestSearch:

    def test_search_aircraft_by_registration(self, menu, aircraft_service, capsys):
        menu._prompt_until_valid = MagicMock(return_value="G-TEST")
        aircraft_service.search_aircraft.return_value = [MagicMock()]
        aircraft_service.get_results_view.return_value = "RESULT VIEW"
        menu._format_results_text = MagicMock(return_value="1 result")

        menu._search_option()

        aircraft_service.search_aircraft.assert_called_once_with(
            "registration", "G-TEST"
        )

        out = capsys.readouterr().out
        assert "Search for an aircraft" in out

class TestAdd:

    def test_add_aircraft_success(self, menu, aircraft_service, capsys):
        new_aircraft = MagicMock()
        menu._prompt_add_aircraft = MagicMock(return_value=new_aircraft)
        aircraft_service.add_aircraft.return_value = 42

        menu._add_option()

        aircraft_service.add_aircraft.assert_called_once_with(new_aircraft)
        out = capsys.readouterr().out
        assert "successfully added" in out
        assert "42" in out

class TestUpdate:

    def test_update_aircraft_success(self, menu, aircraft_service, aircraft, capsys):
        menu._get_aircraft_from_selection = MagicMock(return_value=aircraft)
        updated = MagicMock()
        menu._prompt_update_aircraft = MagicMock(return_value=updated)

        menu._update_option()

        aircraft_service.update_aircraft.assert_called_once_with(updated)
        out = capsys.readouterr().out
        assert "Record successfully updated" in out

class TestDelete:

    def test_delete_aircraft_success(self, menu, aircraft_service, aircraft, capsys):
        menu._prompt_delete_aircraft = MagicMock(return_value=aircraft)

        menu._delete_option()

        aircraft_service.delete_aircraft.assert_called_once_with(aircraft)
        out = capsys.readouterr().out
        assert "successfully deleted" in out

    def test_delete_aircraft_constraint_violation(
        self, menu, aircraft_service, aircraft, capsys
    ):
        menu._prompt_delete_aircraft = MagicMock(return_value=aircraft)
        aircraft_service.delete_aircraft.side_effect = ConstraintViolation()

        menu._delete_option()

        out = capsys.readouterr().out
        assert "Error deleting aircraft" in out

class TestGetAircraftFromSelection:

    def test_get_aircraft_from_selection(self, menu, aircraft_service, aircraft):
        menu._prompt_until_valid = MagicMock(return_value=1)
        aircraft_service.get_aircraft_by_id.return_value = aircraft

        result = menu._get_aircraft_from_selection()

        assert result is aircraft
        aircraft_service.get_aircraft_by_id.assert_called_once_with(1)

    def test_get_aircraft_missing_id_raises(self, menu, aircraft_service):
        bad_aircraft = MagicMock(aircraft_id=None)
        menu._prompt_until_valid = MagicMock(return_value=1)
        aircraft_service.get_aircraft_by_id.return_value = bad_aircraft

        with pytest.raises(ValueError):
            menu._get_aircraft_from_selection()

