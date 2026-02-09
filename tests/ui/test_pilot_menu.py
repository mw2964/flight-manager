import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from flightmanagement.ui.pilot_menu import PilotMenu
from flightmanagement.models.pilot import Pilot
from flightmanagement.error import UserCancelled
from flightmanagement.services.pilot_service import DependentRecords

@pytest.fixture
def pilot_service():
    return MagicMock()

@pytest.fixture
def menu(pilot_service):
    session = MagicMock()
    bindings = MagicMock()
    return PilotMenu(
        session=session,
        bindings=bindings,
        conn=None,
        pilot_service=pilot_service,
    )

@pytest.fixture
def pilot():
    return Pilot(
        staff_member_id=1,
        employee_number="E0001",
        first_name="Jane",
        family_name="Goodall",
        employment_start_date=date(2025, 1, 15),
        employment_end_date=date(2026, 2, 22),
        employment_status="Left",
        license_number="TEST001",
        license_type="TVL",
        license_expiration_date=date(2029, 12, 31)
    )

class TestLoad:

    @patch("flightmanagement.ui.pilot_menu.choice")
    def test_load_routes_to_show(self, mock_choice, menu):
        mock_choice.side_effect = ["show", "back"]
        menu._show_option = MagicMock()

        menu.load()

        menu._show_option.assert_called_once()

    @patch("flightmanagement.ui.pilot_menu.choice")
    def test_load_handles_user_cancelled(self, mock_choice, menu):
        mock_choice.side_effect = ["show", "back"]
        menu._show_option = MagicMock(side_effect=UserCancelled("cancel"))

        menu.load()

        menu._show_option.assert_called_once()

    @patch("flightmanagement.ui.pilot_menu.choice")
    def test_load_exits_on_back(self, mock_choice, menu):
        mock_choice.return_value = "back"

        menu.load()  # should exit cleanly


class TestShow:

    def test_show_prints_pilot_table(self, menu, pilot_service, capsys):
        pilot_service.get_pilot_table.return_value = "PILOT TABLE"

        menu._show_option()

        out = capsys.readouterr().out
        assert "Displaying all pilots" in out
        assert "PILOT TABLE" in out

class TestSearch:

    def test_search_pilot_by_registration(self, menu, pilot_service, capsys):
        menu._prompt_until_valid = MagicMock(return_value="Reed")
        pilot_service.search_pilots.return_value = [MagicMock()]
        pilot_service.get_results_view.return_value = "RESULT VIEW"
        menu._format_results_text = MagicMock(return_value="1 result")

        menu._search_option()

        pilot_service.search_pilots.assert_called_once_with(
            "family_name", "Reed"
        )

        out = capsys.readouterr().out
        assert "Search for a pilot" in out

class TestAdd:

    def test_add_pilot_success(self, menu, pilot_service, capsys):
        new_pilot = MagicMock()
        menu._prompt_add_pilot = MagicMock(return_value=new_pilot)
        pilot_service.add_pilot.return_value = 42

        menu._add_option()

        pilot_service.add_pilot.assert_called_once_with(new_pilot)
        out = capsys.readouterr().out
        assert "successfully added" in out
        assert "42" in out

class TestUpdate:

    def test_update_pilot_success(self, menu, pilot_service, pilot, capsys):
        menu._get_pilot_from_selection = MagicMock(return_value=pilot)
        updated = MagicMock()
        menu._prompt_update_pilot = MagicMock(return_value=updated)

        menu._update_option()

        pilot_service.update_pilot.assert_called_once_with(updated)
        out = capsys.readouterr().out
        assert "Record successfully updated" in out

class TestDelete:

    def test_delete_pilot_success(self, menu, pilot_service, pilot, capsys):
        menu._prompt_delete_pilot = MagicMock(return_value=pilot)

        menu._delete_option()

        pilot_service.delete_pilot.assert_called_once_with(pilot)
        out = capsys.readouterr().out
        assert "successfully deleted" in out

    def test_delete_pilot_constraint_violation(
        self, menu, pilot_service, pilot, capsys
    ):
        menu._prompt_delete_pilot = MagicMock(return_value=pilot)
        pilot_service.delete_pilot.side_effect = DependentRecords()

        menu._delete_option()

        out = capsys.readouterr().out
        assert "Cannot delete pilot" in out

class TestGetPilotFromSelection:

    def test_get_pilot_from_selection(self, menu, pilot_service, pilot):
        menu._prompt_until_valid = MagicMock(return_value=1)
        pilot_service.get_pilot_by_id.return_value = pilot

        result = menu._get_pilot_from_selection()

        assert result is pilot
        pilot_service.get_pilot_by_id.assert_called_once_with(1)

    def test_get_pilot_missing_id_raises(self, menu, pilot_service):
        bad_pilot = MagicMock(staff_member_id=None)
        menu._prompt_until_valid = MagicMock(return_value=1)
        pilot_service.get_pilot_by_id.return_value = bad_pilot

        with pytest.raises(ValueError):
            menu._get_pilot_from_selection()

