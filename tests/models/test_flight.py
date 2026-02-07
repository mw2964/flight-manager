import pytest
from datetime import datetime, date, time
from dataclasses import FrozenInstanceError
from flightmanagement.models.flight import Flight

class TestCreation:

    def test_flight_creation_with_required_fields(self):
        flight = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        assert flight.flight_number == "ZMY111"
        assert flight.origin_location_id == 1
        assert flight.destination_location_id == 2
        assert flight.scheduled_departure_date == date(2026, 1, 15)
        assert flight.scheduled_departure_time == time(15, 30)
        assert flight.scheduled_arrival_date == date(2026, 1, 15)
        assert flight.scheduled_arrival_time == time(18, 30)
        assert flight.flight_status == "Scheduled"

    def test_flight_optional_field_defaults(self):
        flight = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        assert flight.flight_id is None
        assert flight.aircraft_id is None
        assert flight.captain_id is None
        assert flight.first_officer_id is None
        assert flight.confirmed_departure_date is None
        assert flight.confirmed_departure_time is None
        assert flight.confirmed_arrival_date is None
        assert flight.confirmed_arrival_time is None

class TestAttributeValidation:

    @pytest.mark.parametrize("flight_number", ["ZMY1", "ZMY12", "ZMY123", "ZMY1234"])
    def test_valid_flight_numbers_are_accepted(self, flight_number):
        flight = Flight(
            flight_number=flight_number,
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )
        assert flight.flight_number == flight_number

    @pytest.mark.parametrize("flight_number", [None, "", "ZMY", "Z890", "ABC123", "ZMY 123", " ZMY123", "ZMY123 ", "12ZMY3"])
    def test_invalid_flight_number_raises_value_error(self, flight_number):
        with pytest.raises(ValueError, match="Invalid flight number"):
            Flight(
                flight_number=flight_number,
                origin_location_id=1,
                destination_location_id=2,
                scheduled_departure_date=date(2026, 1, 15),
                scheduled_departure_time=time(15, 30),
                scheduled_arrival_date=date(2026, 1, 15),
                scheduled_arrival_time=time(18, 30),
                flight_status="Scheduled"
            )

    def test_scheduled_arrival_before_departure_raises_value_error(self):
        with pytest.raises(ValueError, match="Scheduled arrival time is not later than scheduled departure time"):
            Flight(
                flight_number="ZMY111",
                origin_location_id=1,
                destination_location_id=2,
                scheduled_departure_date=date(2026, 1, 15),
                scheduled_departure_time=time(15, 30),
                scheduled_arrival_date=date(2026, 1, 15),
                scheduled_arrival_time=time(12, 30),
                flight_status="Scheduled"
            )

    def test_actual_arrival_before_departure_raises_value_error(self):
        with pytest.raises(ValueError, match="Actual arrival time is not later than actual departure time"):
            Flight(
                flight_number="ZMY111",
                origin_location_id=1,
                destination_location_id=2,
                scheduled_departure_date=date(2026, 1, 15),
                scheduled_departure_time=time(15, 30),
                scheduled_arrival_date=date(2026, 1, 15),
                scheduled_arrival_time=time(18, 30),
                confirmed_departure_date=date(2026, 1, 15),
                confirmed_departure_time=time(15, 30),
                confirmed_arrival_date=date(2026, 1, 15),
                confirmed_arrival_time=time(12, 30),
                flight_status="Scheduled"
            )

    def test_same_origin_and_destination_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid destination ID"):
            Flight(
                flight_number="ZMY111",
                origin_location_id=1,
                destination_location_id=1,
                scheduled_departure_date=date(2026, 1, 15),
                scheduled_departure_time=time(15, 30),
                scheduled_arrival_date=date(2026, 1, 15),
                scheduled_arrival_time=time(18, 30),
                flight_status="Scheduled"
            )

    def test_same_pilot_and_copilot_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid first officer ID"):
            Flight(
                flight_number="ZMY111",
                origin_location_id=1,
                destination_location_id=2,
                captain_id=1,
                first_officer_id=1,
                scheduled_departure_date=date(2026, 1, 15),
                scheduled_departure_time=time(15, 30),
                scheduled_arrival_date=date(2026, 1, 15),
                scheduled_arrival_time=time(18, 30),
                flight_status="Scheduled"
            )

    def test_invalid_status_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid status"):
            Flight(
                flight_number="ZMY111",
                origin_location_id=1,
                destination_location_id=2,
                scheduled_departure_date=date(2026, 1, 15),
                scheduled_departure_time=time(15, 30),
                scheduled_arrival_date=date(2026, 1, 15),
                scheduled_arrival_time=time(18, 30),
                flight_status="Invalid"
            )

    @pytest.mark.parametrize("status", ["Scheduled", "On time", "Delayed", "Boarding", "Closed", "Departed", "Arrived"])
    def test_valid_statuses_are_accepted(self, status):
        flight = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status=status
        )
        assert flight.flight_status == status

class TestCharacteristics:

    def test_flight_is_immutable(self):
        flight = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        with pytest.raises(FrozenInstanceError):
            flight.status = "Arrived" # type: ignore

    def test_flight_str_representation(self):
        flight = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        assert str(flight) == "ZMY111 (departure: 2026-01-15 15:30, status: Scheduled)"

    def test_flight_equality(self):
        flight1 = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        flight2 = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )
        assert flight1 == flight2

    def test_flight_inequality(self):
        flight1 = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        flight2 = Flight(
            flight_number="ZMY222",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )

        assert flight1 != flight2

    def test_flight_is_hashable(self):
        flight = Flight(
            flight_number="ZMY111",
            origin_location_id=1,
            destination_location_id=2,
            scheduled_departure_date=date(2026, 1, 15),
            scheduled_departure_time=time(15, 30),
            scheduled_arrival_date=date(2026, 1, 15),
            scheduled_arrival_time=time(18, 30),
            flight_status="Scheduled"
        )
        flight_set = {flight}

        assert flight in flight_set



