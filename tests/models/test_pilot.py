import pytest
from dataclasses import FrozenInstanceError
from flightmanagement.models.pilot import Pilot

class TestCreation:

    def test_pilot_creation_with_required_fields(self):
        pilot = Pilot(
            first_name="Jane",
            family_name="Goodall"
        )

        assert pilot.first_name == "Jane"
        assert pilot.family_name == "Goodall"

    def test_pilot_optional_field_defaults(self):
        pilot = Pilot(
            first_name="Jane",
            family_name="Goodall"
        )

        assert pilot.id is None

class TestAttributeValidation:

    @pytest.mark.parametrize("first_name", ["sonia", "Sonia", "Jim-Bob", "Ellie May"])
    def test_valid_first_names_are_accepted(self, first_name):
        pilot = Pilot(
            first_name=first_name,
            family_name="Goodall"
        )

        assert pilot.first_name == first_name

    @pytest.mark.parametrize("first_name", ["", "123", "Jim2", "Jim2Ben", "Jim@Ben"])
    def test_invalid_first_name_raises_value_error(self, first_name):
        with pytest.raises(ValueError, match="Invalid first name"):
            Pilot(
                first_name=first_name,
                family_name="Goodall"
            )

    @pytest.mark.parametrize("family_name", ["smith", "Smith", "Fotherington-Thomas", "Saint John"])
    def test_valid_family_names_are_accepted(self, family_name):
        pilot = Pilot(
            first_name="Jane",
            family_name=family_name
        )

        assert pilot.family_name == family_name

    @pytest.mark.parametrize("family_name", ["", "123", "Jones2", "Jones2Smith", "Jones%Smith"])
    def test_invalid_family_name_raises_value_error(self, family_name):
        with pytest.raises(ValueError, match="Invalid family name"):
            Pilot(
                first_name="Jane",
                family_name=family_name
            )

class TestCharacteristics:

    def test_pilot_is_immutable(self):
        pilot = Pilot(
            first_name="Jane",
            family_name="Goodall"
        )

        with pytest.raises(FrozenInstanceError):
            pilot.first_name = "Jim" # type: ignore

    def test_pilot_str_representation(self):
        pilot = Pilot(
            id=1,
            first_name="Mary Jane",
            family_name="Goodall"
        )

        assert str(pilot) == "Mary Jane Goodall"

    def test_pilot_equality(self):
        pilot1 = Pilot(
            first_name="Jane",
            family_name="Goodall"
        )

        pilot2 = Pilot(
            first_name="Jane",
            family_name="Goodall"
        )

        assert pilot1 == pilot2

    def test_pilot_is_hashable(self):
        pilot = Pilot(
            first_name="Jane",
            family_name="Goodall"
        )
        pilot_set = {pilot}

        assert pilot in pilot_set
