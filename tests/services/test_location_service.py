import pytest
from unittest.mock import MagicMock, patch

from flightmanagement.services.location_service import LocationService
from flightmanagement.models.location import Location

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def service(mock_conn):
    mock_repo = MagicMock()
    return LocationService(mock_conn, location_repository=mock_repo)

@pytest.fixture
def sample_location():
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

class TestAddData:

    @patch("flightmanagement.services.location_service.transaction")
    def test_add_location_inserts_location(self, mock_transaction, service):
        location = Location(
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
        service.add_location(location)

        service._LocationService__location_repository.insert_location.assert_called_once()

class TestUpdateData:

    @patch("flightmanagement.services.location_service.transaction")
    def test_update_location_updates_item(self, mock_transaction, service, sample_location):
        service.update_location(sample_location)
        service._LocationService__location_repository.update_location.assert_called_once()

class TestDeleteData:

    @patch("flightmanagement.services.location_service.transaction")
    def test_delete_location_deletes_item(self, mock_transaction, service, sample_location):
        service.delete_location(sample_location)

        service._LocationService__location_repository.delete_location.assert_called_once_with(sample_location)

class TestUseRepository:

    def test_search_location_calls_repository(self, service):
        service.search_locations("code", "AAA")

        service._LocationService__location_repository.search_on_field.assert_called_once_with(
            "code", "AAA"
        )

    def test_get_location_table_uses_repository(self, service, sample_location):
        service._LocationService__location_repository.get_location_list.return_value = [
            sample_location
        ]

        result = service.get_location_table()

        assert "ABC" in result

class TestReturnData:

    def test_get_location_by_id(self, service):
        service.get_location_by_id(10)

        service._LocationService__location_repository.get_location_by_id.assert_called_once_with(10)

    def test_get_location_choices_returns_tuples(self, service, sample_location):
        service._LocationService__location_repository.get_location_list.return_value = [
            sample_location
        ]

        result = service.get_location_choices()

        assert result == [
            (1, str(sample_location))
        ]

    def test_get_location_choices_empty_list(self, service):
        service._LocationService__location_repository.get_location_list.return_value = []

        result = service.get_location_choices()

        assert result == []

    def test_get_results_view_empty_list(self, service):
        assert service.get_results_view([]) == ""

    def test_get_results_view_none(self, service):
        assert service.get_results_view(None) == ""

    def test_get_results_view_contains_location_data(self, service, sample_location):
        output = service.get_results_view([sample_location])

        assert "ABC" in output
        assert "United Kingdom" in output

