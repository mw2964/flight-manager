import pytest
from unittest.mock import MagicMock
from flightmanagement.services.aircraft_service import AircraftService

@pytest.fixture
def mock_repo(monkeypatch):
    repo = MagicMock()

    monkeypatch.setattr(
        "flightmanagement.services.aircraft_service.AircraftRepository",
        lambda conn: repo
    )

    return repo

@pytest.fixture
def mock_transaction(monkeypatch):
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = None
    mock_ctx.__exit__.return_value = None

    monkeypatch.setattr(
        "flightmanagement.services.aircraft_service.transaction",
        lambda conn: mock_ctx
    )

    return mock_ctx

@pytest.fixture
def service(mock_repo, mock_transaction):
    return AircraftService(conn=MagicMock())

def test_add_aircraft_uses_transaction(service, mock_repo, mock_transaction):
    service.add_aircraft(
        registration="G-TEST",
        manufacturer_serial_no=123,
        icao_hex="ABC",
        manufacturer="Boeing",
        model="737",
        icao_type="B737",
        status="Active"
    )

    mock_transaction.__enter__.assert_called_once()
    mock_transaction.__exit__.assert_called_once()

def test_add_aircraft_creates_aircraft_and_calls_repo(service, mock_repo):
    service.add_aircraft(
        registration="G-TEST",
        manufacturer_serial_no=123,
        icao_hex="ABC",
        manufacturer="Boeing",
        model="737",
        icao_type="B737",
        status="Active"
    )

    mock_repo.add_aircraft.assert_called_once()
    aircraft = mock_repo.add_aircraft.call_args[0][0]

    assert aircraft.registration == "G-TEST"
    assert aircraft.manufacturer == "Boeing"
    assert aircraft.id is None

def test_update_aircraft_passes_correct_aircraft(service, mock_repo):
    service.update_aircraft(
        id=1,
        registration="G-UPD",
        manufacturer_serial_no=999,
        icao_hex="DEF",
        manufacturer="Airbus",
        model="A320",
        icao_type="A320",
        status="Active"
    )

    mock_repo.update_aircraft.assert_called_once()
    aircraft = mock_repo.update_aircraft.call_args[0][0]

    assert aircraft.id == 1
    assert aircraft.model == "A320"

def test_delete_aircraft_calls_repo(service, mock_repo):
    service.delete_aircraft(42)
    mock_repo.delete_aircraft.assert_called_once_with(42)

def test_get_aircraft_by_id_delegates(service, mock_repo):
    mock_repo.get_by_id.return_value = "aircraft"

    result = service.get_aircraft_by_id(1)

    mock_repo.get_by_id.assert_called_once_with(1)
    assert result == "aircraft"

def test_search_aircraft_delegates(service, mock_repo):
    mock_repo.search_on_field.return_value = []

    result = service.search_aircraft("manufacturer", "Boeing")

    mock_repo.search_on_field.assert_called_once_with("manufacturer", "Boeing")
    assert result == []

def test_get_aircraft_choices_empty(service, mock_repo):
    mock_repo.get_aircraft_list.return_value = None

    result = service.get_aircraft_choices()

    assert result == []

from flightmanagement.models.aircraft import Aircraft

def test_get_aircraft_choices_populated(service, mock_repo):
    a1 = Aircraft(
        id=1,
        registration="G-ONE",
        manufacturer_serial_no=1,
        icao_hex="A",
        manufacturer="B",
        model="C",
        icao_type="D",
        status="Active"
    )
    a2 = Aircraft(
        id=2,
        registration="G-TWO",
        manufacturer_serial_no=2,
        icao_hex="B",
        manufacturer="C",
        model="D",
        icao_type="E",
        status="Inactive"
    )

    mock_repo.get_aircraft_list.return_value = [a1, a2]

    result = service.get_aircraft_choices()

    assert result == [
        (1, str(a1) + " - Active"),
        (2, str(a2) + " - Inactive")
    ]

def test_get_aircraft_table_none_returns_empty(service, mock_repo):
    mock_repo.get_aircraft_list.return_value = None

    assert service.get_aircraft_table() == ""

def test_get_aircraft_table_formats_output(service, mock_repo):
    aircraft = Aircraft(
        id=1,
        registration="G-TBL",
        manufacturer_serial_no=123,
        icao_hex="HEX",
        manufacturer="Boeing",
        model="737",
        icao_type="B737",
        status="Active"
    )
    mock_repo.get_aircraft_list.return_value = [aircraft]

    table = service.get_aircraft_table()

    assert "G-TBL" in table
    assert "Boeing" in table
    assert table.startswith("     ")

def test_get_results_view_none_or_empty_list_returns_empty(service):
    assert service.get_results_view(None) == ""
    assert service.get_results_view([]) == ""
