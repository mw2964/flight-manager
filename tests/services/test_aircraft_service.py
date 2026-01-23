import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.models.aircraft import Aircraft

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def service(mock_conn):
    mock_repo = MagicMock()
    return AircraftService(mock_conn, aircraft_repository=mock_repo)

@pytest.fixture
def sample_aircraft():
    return Aircraft(
        id=1,
        registration="G-ABCD",
        manufacturer_serial_no=12345,
        icao_hex="406ABC",
        manufacturer="Airbus",
        model="A320",
        icao_type="A320",
        status="Active"
    )

class TestAddData:

    @patch("flightmanagement.services.aircraft_service.transaction")
    def test_add_aircraft_inserts_aircraft(self, mock_transaction, service):        
        aircraft = Aircraft(
            registration="G-TEST",
            manufacturer_serial_no=111,
            icao_hex="406FFF",
            manufacturer="Boeing",
            model="737",
            icao_type="B737",
            status="Active"
        )
        service.add_aircraft(aircraft)

        service._AircraftService__aircraft_repository.insert_item.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.aircraft_service.transaction")
    def test_update_aircraft_updates_item(self, mock_transaction, service, sample_aircraft):
        service.update_aircraft(sample_aircraft)

        service._AircraftService__aircraft_repository.update_item.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.aircraft_service.transaction")
    def test_delete_aircraft_deletes_item(self, mock_transaction, service, sample_aircraft):
        service.delete_aircraft(sample_aircraft)

        service._AircraftService__aircraft_repository.delete_item.assert_called_once_with(sample_aircraft)

class TestUseRepository:

    def test_search_aircraft_calls_repository(self, service):
        service.search_aircraft("registration", "G-ABCD")

        service._AircraftService__aircraft_repository.search_on_field.assert_called_once_with(
            "registration", "G-ABCD"
        )

    def test_get_aircraft_table_uses_repository(self, service, sample_aircraft):
        service._AircraftService__aircraft_repository.get_aircraft_list.return_value = [
            sample_aircraft
        ]

        result = service.get_aircraft_table()

        assert "G-ABCD" in result

class TestReturnData:

    def test_get_aircraft_by_id(self, service):
        service.get_aircraft_by_id(10)

        service._AircraftService__aircraft_repository.get_item_by_id.assert_called_once_with(10)

    def test_get_aircraft_choices_returns_tuples(self, service, sample_aircraft):
        service._AircraftService__aircraft_repository.get_aircraft_list.return_value = [
            sample_aircraft
        ]

        result = service.get_aircraft_choices()

        assert result == [
            (1, f"{str(sample_aircraft)} - {sample_aircraft.status}")
        ]

    def test_get_aircraft_choices_empty_list(self, service):
        service._AircraftService__aircraft_repository.get_aircraft_list.return_value = []

        result = service.get_aircraft_choices()

        assert result == []

    def test_get_results_view_empty_list(self, service):
        assert service.get_results_view([]) == ""

    def test_get_results_view_none(self, service):
        assert service.get_results_view(None) == ""

    def test_get_results_view_contains_aircraft_data(self, service, sample_aircraft):
        output = service.get_results_view([sample_aircraft])

        assert "G-ABCD" in output
        assert "Airbus" in output
        assert "A320" in output
        assert "Active" in output


