import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.services.aircraft_service import AircraftService
from flightmanagement.models.aircraft import Aircraft, AircraftType

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
        aircraft_id=1,
        aircraft_type_id=1,
        registration="G-ABCD",
        manufacturer_serial_no=269785,
        icao_hex="406ABC",
        aircraft_status="Active"
    )

@pytest.fixture
def sample_aircraft_type():
    return AircraftType(
        aircraft_type_id=1,
        manufacturer="Boeing",
        model="777-300ER",
        icao_type="B77W"
    )

class TestAddData:

    @patch("flightmanagement.services.aircraft_service.transaction")
    def test_add_aircraft_inserts_aircraft(self, mock_transaction, service):        
        aircraft = Aircraft(            
            aircraft_type_id=1,
            registration="G-ABCD",
            manufacturer_serial_no=269785,
            icao_hex="406ABC",
            aircraft_status="Active"
        )
        service.add_aircraft(aircraft)

        service._AircraftService__aircraft_repository.insert_aircraft.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.aircraft_service.transaction")
    def test_update_aircraft_updates_item(self, mock_transaction, service, sample_aircraft):
        service.update_aircraft(sample_aircraft)

        service._AircraftService__aircraft_repository.update_aircraft.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.aircraft_service.transaction")
    def test_delete_aircraft_deletes_item(self, mock_transaction, service, sample_aircraft):
        service.delete_aircraft(sample_aircraft)

        service._AircraftService__aircraft_repository.delete_aircraft.assert_called_once_with(sample_aircraft)

class TestUseRepository:

    def test_search_aircraft_calls_repository(self, service):
        service.search_aircraft("registration", "G-ABCD")

        service._AircraftService__aircraft_repository.search_aircraft_on_field.assert_called_once_with(
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

        service._AircraftService__aircraft_repository.get_aircraft_by_id.assert_called_once_with(10)

    def test_get_aircraft_choices_returns_tuples(self, service, sample_aircraft, sample_aircraft_type):
        service._AircraftService__aircraft_repository.get_aircraft_list.return_value = [
            sample_aircraft
        ]
        service._AircraftService__aircraft_repository.get_aircraft_type_by_id.return_value =sample_aircraft_type

        result = service.get_aircraft_choices()

        assert result == [
            (1, f"{sample_aircraft.registration} ({sample_aircraft_type.manufacturer} {sample_aircraft_type.model}) - {sample_aircraft.aircraft_status}")
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
        assert "269785" in output
        assert "406ABC" in output
        assert "Active" in output


