import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from flightmanagement.ui.location_menu import LocationMenu
from flightmanagement.models.location import Location
from flightmanagement.error import UserCancelled
from flightmanagement.services.location_service import ConstraintViolation

@pytest.fixture
def location_service():
    return MagicMock()

@pytest.fixture
def menu(location_service):
    session = MagicMock()
    bindings = MagicMock()
    return LocationMenu(
        session=session,
        bindings=bindings,
        conn=None,
        location_service=location_service,
    )

@pytest.fixture
def location():
    return Location(
        location_id=1,
        location_type="Airport",
        icao_location_code="ABCD",
        iata_airport_code="ABC",
        location_name="Test Airport",
        town_or_city="Milton Keynes",
        state_or_county="Buckinghamshire",
        country="United Kingdom",
        geographic_region="Europe",
        decimal_latitude=-45.30,
        decimal_longitude=112.30
    )

class TestLoad:

    @patch("flightmanagement.ui.location_menu.choice")
    def test_load_routes_to_show(self, mock_choice, menu):
        mock_choice.side_effect = ["show", "back"]
        menu._show_option = MagicMock()

        menu.load()

        menu._show_option.assert_called_once()

    @patch("flightmanagement.ui.location_menu.choice")
    def test_load_handles_user_cancelled(self, mock_choice, menu):
        mock_choice.side_effect = ["show", "back"]
        menu._show_option = MagicMock(side_effect=UserCancelled("cancel"))

        menu.load()

        menu._show_option.assert_called_once()

    @patch("flightmanagement.ui.location_menu.choice")
    def test_load_exits_on_back(self, mock_choice, menu):
        mock_choice.return_value = "back"

        menu.load()  # should exit cleanly


class TestShow:

    def test_show_prints_location_table(self, menu, location_service, capsys):
        location_service.get_location_table.return_value = "LOCATION TABLE"

        menu._show_option()

        out = capsys.readouterr().out
        assert "Displaying all destinations" in out
        assert "LOCATION TABLE" in out

class TestSearch:

    def test_search_location_by_code(self, menu, location_service, capsys):
        menu._prompt_until_valid = MagicMock(return_value="ABC")
        location_service.search_locations.return_value = [MagicMock()]
        location_service.get_results_view.return_value = "RESULT VIEW"
        menu._format_results_text = MagicMock(return_value="1 result")

        menu._search_option()

        location_service.search_locations.assert_called_once_with(
            "iata_airport_code", "ABC"
        )

        out = capsys.readouterr().out
        assert "Search for a destination" in out

class TestAdd:

    def test_add_location_success(self, menu, location_service, capsys):
        new_location = MagicMock()
        menu._prompt_add_location = MagicMock(return_value=new_location)
        location_service.add_location.return_value = 42

        menu._add_option()

        location_service.add_location.assert_called_once_with(new_location)
        out = capsys.readouterr().out
        assert "successfully added" in out
        assert "42" in out

class TestUpdate:

    def test_update_location_success(self, menu, location_service, location, capsys):
        menu._get_location_from_selection = MagicMock(return_value=location)
        updated = MagicMock()
        menu._prompt_update_location = MagicMock(return_value=updated)

        menu._update_option()

        location_service.update_location.assert_called_once_with(updated)
        out = capsys.readouterr().out
        assert "Record successfully updated" in out

class TestDelete:

    def test_delete_location_success(self, menu, location_service, location, capsys):
        menu._prompt_delete_location = MagicMock(return_value=location)

        menu._delete_option()

        location_service.delete_location.assert_called_once_with(location)
        out = capsys.readouterr().out
        assert "successfully deleted" in out

    def test_delete_location_constraint_violation(
        self, menu, location_service, location, capsys
    ):
        menu._prompt_delete_location = MagicMock(return_value=location)
        location_service.delete_location.side_effect = ConstraintViolation()

        menu._delete_option()

        out = capsys.readouterr().out
        assert "Error deleting destination" in out

class TestGetLocationFromSelection:

    def test_get_location_from_selection(self, menu, location_service, location):
        menu._prompt_until_valid = MagicMock(return_value=1)
        location_service.get_location_by_id.return_value = location

        result = menu._get_location_from_selection()

        assert result is location
        location_service.get_location_by_id.assert_called_once_with(1)

    def test_get_location_missing_id_raises(self, menu, location_service):
        bad_location = MagicMock(location_id=None)
        menu._prompt_until_valid = MagicMock(return_value=1)
        location_service.get_location_by_id.return_value = bad_location

        with pytest.raises(ValueError):
            menu._get_location_from_selection()
