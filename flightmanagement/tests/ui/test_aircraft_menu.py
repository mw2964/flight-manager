import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_service(monkeypatch):
    return MagicMock()

@pytest.fixture
def mock_prompt(monkeypatch):
    def _responses(values):
        it = iter(values)

        def fake_prompt(*args, **kwargs):
            value = next(it)
            if value == "__CANCEL__":
                return None   # emulate prompt_or_cancel behaviour
            return value

        monkeypatch.setattr(
            "flightmanagement.ui.aircraft_menu.prompt_or_cancel",
            fake_prompt
        )

    return _responses

@pytest.fixture
def mock_choice(monkeypatch):
    def _set_choices(choices):
        iterator = iter(choices)

        def fake_choice(*args, **kwargs):
            return next(iterator)

        monkeypatch.setattr(
            "flightmanagement.ui.aircraft_menu.choice",
            fake_choice
        )

    return _set_choices

from flightmanagement.ui.aircraft_menu import AircraftMenu

@pytest.fixture
def menu(mock_service):
    return AircraftMenu(
        session=MagicMock(),
        bindings=MagicMock(),
        aircraft_service=mock_service
    )

def test_show_option_prints_table(menu, mock_service, capsys):
    mock_service.get_aircraft_table.return_value = "TABLE"

    menu._AircraftMenu__show_option()

    out = capsys.readouterr().out
    assert "Displaying all aircraft" in out
    assert "TABLE" in out

def test_search_cancelled(menu, mock_prompt):
    mock_prompt(["__CANCEL__"])

    result = menu._AircraftMenu__search_option()

    assert result is False

def test_search_no_results(menu, mock_prompt, mock_service, capsys):
    mock_prompt(["G-TEST"])
    mock_service.search_aircraft.return_value = []

    result = menu._AircraftMenu__search_option()

    out = capsys.readouterr().out
    assert "No matching results" in out
    assert result is True

def test_search_with_results(menu, mock_prompt, mock_service):
    mock_prompt(["G-TEST"])
    mock_service.search_aircraft.return_value = ["aircraft"]
    mock_service.get_results_view.return_value = "RESULTS"

    result = menu._AircraftMenu__search_option()

    mock_service.get_results_view.assert_called_once()
    assert result is True

def test_add_aircraft_success(menu, mock_prompt, mock_service):
    mock_prompt([
        "G-TEST",      # registration
        "123",         # msn
        "HEX",
        "Boeing",
        "737",
        "B737",
        "Active"
    ])

    result = menu._AircraftMenu__add_option()

    mock_service.add_aircraft.assert_called_once()
    assert result is True

def test_add_aircraft_cancelled(menu, mock_prompt, mock_service):
    mock_prompt(["__CANCEL__"])

    result = menu._AircraftMenu__add_option()

    mock_service.add_aircraft.assert_not_called()
    assert result is False

def test_add_aircraft_invalid_serial_then_valid(menu, mock_prompt, mock_service):
    mock_prompt([
        "G-TEST",
        "abc",     # invalid
        "123",     # valid
        "HEX",
        "Boeing",
        "737",
        "B737",
        "Active"
    ])

    result = menu._AircraftMenu__add_option()

    assert result is True
    mock_service.add_aircraft.assert_called_once()

def test_update_cancelled_at_choice(menu, mock_choice):
    mock_choice(["__CANCEL__"])

    result = menu._AircraftMenu__update_option()

    assert result is False

from flightmanagement.models.aircraft import Aircraft

def test_update_aircraft_success(menu, mock_choice, mock_prompt, mock_service):
    aircraft = Aircraft(
        id=1,
        registration="G-OLD",
        manufacturer_serial_no=1,
        icao_hex="HEX",
        manufacturer="B",
        model="M",
        icao_type="T",
        status="Active"
    )
    
    mock_service.get_aircraft_by_id.return_value = aircraft

    mock_choice([1, "Active"])
    mock_prompt([
        "G-NEW",
        "123",
        "HEX",
        "Boeing",
        "737",
        "B737"
    ])

    result = menu._AircraftMenu__update_option()

    mock_service.update_aircraft.assert_called_once()
    assert result is True

def test_delete_cancelled(menu, mock_choice, mock_service):
    mock_choice(["__CANCEL__"])

    result = menu._AircraftMenu__delete_option()

    mock_service.delete_aircraft.assert_not_called()
    assert result is False

def test_delete_confirmed(menu, mock_choice, mock_service):
    mock_choice([1, 1])  # select aircraft, confirm yes

    result = menu._AircraftMenu__delete_option()

    mock_service.delete_aircraft.assert_called_once()
    assert result is True

def test_load_back_exits(menu, mock_choice):
    mock_choice(["back"])

    menu.load()  # should return cleanly

