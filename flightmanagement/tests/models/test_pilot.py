from flightmanagement.models.pilot import Pilot

def test_pilot_initialization():
    pilot = Pilot(id=1, first_name="John", family_name="Doe")

    assert pilot.id == 1
    assert pilot.first_name == "John"
    assert pilot.family_name == "Doe"

