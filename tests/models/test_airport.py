import pytest
from dataclasses import FrozenInstanceError
from flightmanagement.models.airport import Airport

class TestCreation:

    def test_airport_creation_with_required_fields(self):
        airport = Airport(
            code="XXX"
        )

        assert airport.code == "XXX"

    def test_airport_optional_field_defaults(self):
        airport = Airport(
            code="XXX"
        )

        assert airport.id is None
        assert airport.name is None
        assert airport.city is None
        assert airport.country is None
        assert airport.region is None

class TestAttributeValidation:

    def test_valid_codes_are_accepted(self):
        airport = Airport(
            code="ABC"
        )

        assert airport.code == "ABC"

    @pytest.mark.parametrize("code", [None, "", "123", "abc", "ABCD", "AB", "A-B"])
    def test_invalid_code_raises_value_error(self, code):
        with pytest.raises(ValueError, match="Invalid code"):
            Airport(
                code=code
            )

class TestCharacteristics:

    def test_airport_is_immutable(self):
        airport = Airport(
            id=1,
            code="XXX",
            name="Xanadu International",
            city="Xanadu",
            country="Mongolia",
            region="Asia"
        )

        with pytest.raises(FrozenInstanceError):
            airport.name = "Xanadu International Airport" # type: ignore

    def test_airport_str_representation(self):
        airport = Airport(
            id=1,
            code="XXX",
            name="Xanadu International",
            city="Xanadu",
            country="Mongolia",
            region="Asia"
        )

        assert str(airport) == "XXX (Xanadu International)"

    def test_airport_equality(self):
        airport1 = Airport(
            code="XXX"
        )

        airport2 = Airport(
            code="XXX"
        )
        assert airport1 == airport2

    def test_airport_inequality(self):
        airport1 = Airport(
            code="XXX"
        )

        airport2 = Airport(
            code="YYY"
        )
        assert airport1 != airport2

    def test_airport_is_hashable(self):
        airport = Airport(
            code="XXX"
        )
        airport_set = {airport}

        assert airport in airport_set
