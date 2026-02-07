import pytest
from dataclasses import FrozenInstanceError
from flightmanagement.error import FieldValidationError, DomainValidationError
from flightmanagement.models.location import Location

class TestCreation:

    def test_airport_location_creation_with_required_fields(self):
        location = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )

        assert location.location_type == "Airport"
        assert location.location_name == "Test Airport"
        assert location.iata_airport_code == "XXX"
        assert location.town_or_city == "Test City"
        assert location.country == "Test Country"
    
    def test_non_airport_location_creation_with_required_fields(self):
        location = Location(
            location_type="Airfield",
            location_name="Test Airfield",
            icao_location_code="XXXX",
            country="Test Country"
        )

        assert location.location_type == "Airfield"
        assert location.location_name == "Test Airfield"
        assert location.icao_location_code == "XXXX"
        assert location.country == "Test Country"

    def test_airport_optional_field_defaults(self):
        location = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )

        assert location.location_id is None
        assert location.icao_location_code is None
        assert location.state_or_county is None
        assert location.geographic_region is None
        assert location.decimal_latitude is None
        assert location.decimal_longitude is None

    def test_non_airport_optional_field_defaults(self):
        location = Location(
            location_type="Airfield",
            location_name="Test Airfield",
            icao_location_code="XXXX",
            country="Test Country"
        )

        assert location.location_id is None
        assert location.iata_airport_code is None
        assert location.town_or_city is None
        assert location.state_or_county is None
        assert location.geographic_region is None
        assert location.decimal_latitude is None
        assert location.decimal_longitude is None

class TestAttributeValidation:

    def test_valid_airport_codes_are_accepted(self):
        location = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="ABC",
            town_or_city="Test City",
            country="Test Country"
        )

        assert location.iata_airport_code == "ABC"

    @pytest.mark.parametrize("code", [None, "", "123", "abc", "ABCD", "AB", "A-B"])
    def test_invalid_airport_code_raises_value_error(self, code):
        with pytest.raises(FieldValidationError):
            location = Location(
                location_type="Airport",
                location_name="Test Airport",
                iata_airport_code=code,
                town_or_city="Test City",
                country="Test Country"
            )

    def test_valid_location_codes_are_accepted(self):
        location = Location(
            location_type="Airfield",
            location_name="Test Airfield",
            icao_location_code="ABCD",
            country="Test Country"
        )

        assert location.icao_location_code == "ABCD"

    @pytest.mark.parametrize("code", [None, "", "1234", "abcd", "ABC", "AB", "A-BC"])
    def test_invalid_location_code_raises_value_error(self, code):
        with pytest.raises(FieldValidationError):
            location = Location(
                location_type="Airfield",
                location_name="Test Airfield",
                icao_location_code=code,
                country="Test Country"
            )

class TestCharacteristics:

    def test_airport_is_immutable(self):
        location = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )

        with pytest.raises(FrozenInstanceError):
            location.location_name = "Test Airport" # type: ignore

    def test_airport_str_representation(self):
        location = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )

        assert str(location) == "XXX (Test Airport)"

    def test_airport_equality(self):
        location1 = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )

        location2 = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )
        assert location1 == location2

    def test_airport_inequality(self):
        location1 = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )

        location2 = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="YYY",
            town_or_city="Test City",
            country="Test Country"
        )
        assert location1 != location2

    def test_airport_is_hashable(self):
        location = Location(
            location_type="Airport",
            location_name="Test Airport",
            iata_airport_code="XXX",
            town_or_city="Test City",
            country="Test Country"
        )
        location_set = {location}

        assert location in location_set
