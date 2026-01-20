import pytest
from dataclasses import FrozenInstanceError
from flightmanagement.models.aircraft import Aircraft

def test_aircraft_creation_with_required_fields():
    aircraft = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320"
    )

    assert aircraft.registration == "G-TEST"
    assert aircraft.manufacturer == "Airbus"
    assert aircraft.model == "A320"
    assert aircraft.status == "Active"

def test_aircraft_optional_field_defaults():
    aircraft = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320"
    )

    assert aircraft.id is None
    assert aircraft.manufacturer_serial_no is None
    assert aircraft.icao_hex is None
    assert aircraft.icao_type is None

def test_invalid_registration_raises_value_error():
    with pytest.raises(ValueError, match="Invalid registration"):
        Aircraft(
            registration="",
            manufacturer="Airbus",
            model="A320"
        )

def test_invalid_manufacturer_raises_value_error():
    with pytest.raises(ValueError, match="Invalid manufacturer"):
        Aircraft(
            registration="G-TEST",
            manufacturer="",
            model="A320"
        )

def test_invalid_model_raises_value_error():
    with pytest.raises(ValueError, match="Invalid model"):
        Aircraft(
            registration="G-TEST",
            manufacturer="Airbus",
            model=""
        )

def test_invalid_status_raises_value_error():
    with pytest.raises(ValueError, match="Invalid status"):
        Aircraft(
            registration="G-TEST",
            manufacturer="Airbus",
            model="A320",
            status="Invalid"
        )

@pytest.mark.parametrize("status", ["Active", "Inactive", "Decommissioned"])
def test_valid_statuses_are_accepted(status):
    aircraft = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320",
        status=status
    )
    assert aircraft.status == status

def test_aircraft_is_immutable():
    aircraft = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320"
    )

    with pytest.raises(FrozenInstanceError):
        aircraft.status = "Inactive" # type: ignore

def test_aircraft_str_representation():
    aircraft = Aircraft(
        id=1,
        registration="G-TEST",
        manufacturer_serial_no=12345,
        icao_hex="HL87K7",
        manufacturer="Airbus",
        model="A320",
        icao_type="A320",
        status="Active"
    )

    assert str(aircraft) == "G-TEST (Airbus A320)"

def test_aircraft_equality():
    aircraft1 = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320"
    )

    aircraft2 = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320"
    )

    assert aircraft1 == aircraft2

def test_aircraft_is_hashable():
    aircraft = Aircraft(
        registration="G-TEST",
        manufacturer="Airbus",
        model="A320"
    )
    aircraft_set = {aircraft}

    assert aircraft in aircraft_set
