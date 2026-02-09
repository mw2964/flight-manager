import pytest
from datetime import date
from dataclasses import FrozenInstanceError
from flightmanagement.models.pilot import Pilot
from flightmanagement.error import FieldValidationError, DomainValidationError

class TestCreation:

    def test_pilot_creation_with_required_fields(self):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert pilot.employee_number == "E0001"
        assert pilot.first_name == "Jane"
        assert pilot.family_name == "Goodall"
        assert pilot.employment_start_date == date(2025, 1, 15)
        assert pilot.employment_status == "Current"

    def test_pilot_optional_field_defaults(self):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert pilot.staff_member_id is None
        assert pilot.employment_end_date is None
        assert pilot.license_number is None
        assert pilot.license_type is None
        assert pilot.license_expiration_date is None

class TestAttributeValidation:

    @pytest.mark.parametrize("first_name", ["sonia", "Sonia", "Jim-Bob", "Ellie May"])
    def test_valid_first_names_are_accepted(self, first_name):
        pilot = Pilot(
            employee_number="E0001",
            first_name=first_name,
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert pilot.first_name == first_name

    @pytest.mark.parametrize("first_name", ["", "123", "Jim2", "Jim2Ben", "Jim@Ben"])
    def test_invalid_first_name_raises_value_error(self, first_name):
        with pytest.raises(FieldValidationError):
            Pilot(
                employee_number="E0001",
                first_name=first_name,
                family_name="Goodall",
                employment_start_date=date(2025, 1, 15),
                employment_status="Current"
            )

    @pytest.mark.parametrize("family_name", ["smith", "Smith", "Fotherington-Thomas", "Saint John"])
    def test_valid_family_names_are_accepted(self, family_name):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name=family_name,
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert pilot.family_name == family_name

    @pytest.mark.parametrize("family_name", ["", "123", "Jones2", "Jones2Smith", "Jones%Smith"])
    def test_invalid_family_name_raises_value_error(self, family_name):
        with pytest.raises(FieldValidationError):
            Pilot(
                employee_number="E0001",
                first_name="Jane",
                family_name=family_name,
                employment_start_date=date(2025, 1, 15),
                employment_status="Current"
            )

class TestCharacteristics:

    def test_pilot_is_immutable(self):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        with pytest.raises(FrozenInstanceError):
            pilot.first_name = "Jane" # type: ignore

    def test_pilot_str_representation(self):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert str(pilot) == "Jane Goodall"

    def test_pilot_equality(self):
        pilot1 = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        pilot2 = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert pilot1 == pilot2

    def test_pilot_inequality(self):
        pilot1 = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        pilot2 = Pilot(
            employee_number="E0001",
            first_name="Bob",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )

        assert pilot1 != pilot2

    def test_pilot_is_hashable(self):
        pilot = Pilot(
            employee_number="E0001",
            first_name="Jane",
            family_name="Goodall",
            employment_start_date=date(2025, 1, 15),
            employment_status="Current"
        )
        pilot_set = {pilot}

        assert pilot in pilot_set
