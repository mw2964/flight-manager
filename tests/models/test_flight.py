import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError
from flightmanagement.models.flight import Flight

class TestCreation:

    def test_flight_creation_with_required_fields(self):
        flight = Flight(
            flight_number="ZMY111",
            aircraft_id=3,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )

        assert flight.flight_number == "ZMY111"
        assert flight.aircraft_id == 3
        assert flight.origin_id == 1
        assert flight.destination_id == 2

    def test_flight_optional_field_defaults(self):
        flight = Flight(
            flight_number="ZMY111",
            aircraft_id=3,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )

        assert flight.id is None
        assert flight.pilot_id is None
        assert flight.copilot_id is None
        assert flight.arrival_time_scheduled is None
        assert flight.departure_time_actual is None
        assert flight.arrival_time_actual is None
        assert flight.status == "Scheduled"

class TestAttributeValidation:

    @pytest.mark.parametrize("flight_number", ["ZMY1", "ZMY12", "ZMY123", "ZMY1234"])
    def test_valid_flight_numbers_are_accepted(self, flight_number):
        flight = Flight(
            flight_number=flight_number,
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )
        assert flight.flight_number == flight_number

    @pytest.mark.parametrize("flight_number", [None, "", "ZMY", "Z890", "ABC123", "ZMY 123", " ZMY123", "ZMY123 ", "12ZMY3"])
    def test_invalid_flight_number_raises_value_error(self, flight_number):
        with pytest.raises(ValueError, match="Invalid flight number"):
            Flight(
                flight_number=flight_number,
                aircraft_id=1,
                origin_id=1,
                destination_id=2,
                departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
            )

    def test_scheduled_arrival_before_departure_raises_value_error(self):
        with pytest.raises(ValueError, match="Scheduled arrival time is not later than scheduled departure time"):
            Flight(
                flight_number="ZMY123",
                aircraft_id=1,
                origin_id=1,
                destination_id=2,
                departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
                arrival_time_scheduled=datetime(2026, 1, 15, 8, 30)
            )

    def test_actual_arrival_before_departure_raises_value_error(self):
        with pytest.raises(ValueError, match="Actual arrival time is not later than actual departure time"):
            Flight(
                flight_number="ZMY123",
                aircraft_id=1,
                origin_id=1,
                destination_id=2,
                departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
                departure_time_actual=datetime(2026, 1, 15, 8, 30),
                arrival_time_actual=datetime(2026, 1, 15, 8, 30)
            )

    def test_same_origin_and_destination_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid destination ID"):
            Flight(
                flight_number="ZMY123",
                aircraft_id=1,
                origin_id=1,
                destination_id=1,
                departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
            )

    def test_same_pilot_and_copilot_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid copilot ID"):
            Flight(
                flight_number="ZMY123",
                aircraft_id=1,
                origin_id=1,
                destination_id=2,
                departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
                pilot_id=1,
                copilot_id=1
            )

    def test_invalid_status_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid status"):
            Flight(
                flight_number="ZMY111",
                aircraft_id=3,
                origin_id=1,
                destination_id=2,
                departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
                status="Invalid"
            )

    @pytest.mark.parametrize("status", ["Scheduled", "On time", "Delayed", "Boarding", "Closed", "Departed", "Arrived"])
    def test_valid_statuses_are_accepted(self, status):
        flight = Flight(
            flight_number="ZMY111",
            aircraft_id=3,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
            status=status
        )
        assert flight.status == status

class TestCharacteristics:

    def test_flight_is_immutable(self):
        flight = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
            status="Scheduled"
        )

        with pytest.raises(FrozenInstanceError):
            flight.status = "Arrived" # type: ignore

    def test_flight_str_representation(self):
        flight = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30),
            status="Scheduled"
        )

        assert str(flight) == "ZMY123 (departure: 2026-01-15 08:30, status: Scheduled)"

    def test_flight_equality(self):
        flight1 = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )

        flight2 = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )

        assert flight1 == flight2

    def test_flight_inequality(self):
        flight1 = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )

        flight2 = Flight(
            flight_number="ZMY124",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )

        assert flight1 != flight2

    def test_flight_is_hashable(self):
        flight = Flight(
            flight_number="ZMY123",
            aircraft_id=1,
            origin_id=1,
            destination_id=2,
            departure_time_scheduled=datetime(2026, 1, 15, 8, 30)
        )
        flight_set = {flight}

        assert flight in flight_set



