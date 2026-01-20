import pytest
from dataclasses import FrozenInstanceError
from flightmanagement.models.airport import Airport

def test_airport_creation_with_required_fields():
    airport = Airport(
        code="XXX"
    )

    assert airport.code == "XXX"

def test_airport_optional_field_defaults():
    airport = Airport(
        code="XXX"
    )

    assert airport.id is None
    assert airport.name is None
    assert airport.city is None
    assert airport.country is None
    assert airport.region is None

def test_valid_codes_are_accepted():
    airport = Airport(
        code="ABC"
    )

    assert airport.code == "ABC"

@pytest.mark.parametrize("code", [None, "", "123", "abc", "ABCD", "AB", "A-B"])
def test_invalid_code_raises_value_error(code):
    with pytest.raises(ValueError, match="Invalid code"):
        Airport(
            code=code
        )

def test_airport_is_immutable():
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

def test_airport_str_representation():
    airport = Airport(
        id=1,
        code="XXX",
        name="Xanadu International",
        city="Xanadu",
        country="Mongolia",
        region="Asia"
    )

    assert str(airport) == "XXX (Xanadu International)"

def test_airport_equality():
    airport1 = Airport(
        code="XXX"
    )

    airport2 = Airport(
        code="XXX"
    )
    assert airport1 == airport2

def test_airport_inequality():
    airport1 = Airport(
        code="XXX"
    )

    airport2 = Airport(
        code="YYY"
    )
    assert airport1 != airport2

def test_airport_is_hashable():
    airport = Airport(
        code="XXX"
    )
    airport_set = {airport}

    assert airport in airport_set
