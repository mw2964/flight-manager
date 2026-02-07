import pytest
from dataclasses import FrozenInstanceError
from flightmanagement.models.aircraft import Aircraft

class TestCreation:

    def test_aircraft_creation_with_required_fields(self):
        aircraft = Aircraft(
            aircraft_type_id=1,
            registration="G-TEST",
            aircraft_status="Active"
        )

        assert aircraft.aircraft_type_id == 1
        assert aircraft.registration == "G-TEST"
        assert aircraft.aircraft_status == "Active"

    def test_aircraft_optional_field_defaults(self):
        aircraft = Aircraft(
            aircraft_type_id=1,
            registration="G-TEST",
            aircraft_status="Active"
        )

        assert aircraft.aircraft_id is None
        assert aircraft.manufacturer_serial_no is None
        assert aircraft.icao_hex is None

class TestAttributeValidation:

    def test_invalid_registration_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid registration"):
            Aircraft(
                aircraft_type_id=1,
                registration="",
                aircraft_status="Active"
            )

    def test_invalid_status_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid status"):
            Aircraft(
                aircraft_type_id=1,
                registration="G-TEST",
                aircraft_status="Invalid"
            )

    @pytest.mark.parametrize("status", ["Active", "Inactive", "Decommissioned"])
    def test_valid_statuses_are_accepted(self, status):
        aircraft = Aircraft(
                aircraft_type_id=1,
                registration="G-TEST",
                aircraft_status=status
        )
        assert aircraft.aircraft_status == status

class TestCharacteristics:

    def test_aircraft_is_immutable(self):
        aircraft = Aircraft(
            aircraft_type_id=1,
            registration="G-TEST",
            aircraft_status="Active"
        )

        with pytest.raises(FrozenInstanceError):
            aircraft.status = "Inactive" # type: ignore

    def test_aircraft_str_representation(self):
        aircraft = Aircraft(
            aircraft_type_id=1,
            registration="G-TEST",
            manufacturer_serial_no=12345,
            icao_hex="HEX",
            aircraft_status="Active"
        )

        assert str(aircraft) == "G-TEST"

    def test_aircraft_equality(self):
        aircraft1 = Aircraft(
            aircraft_type_id=1,
            registration="G-TEST",
            aircraft_status="Active"
        )

        aircraft2 = Aircraft(
            aircraft_type_id=1,
            registration="G-TEST",
            aircraft_status="Active"
        )

        assert aircraft1 == aircraft2

