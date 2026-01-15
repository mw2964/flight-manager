from dataclasses import dataclass

@dataclass
class Pilot:
    id: int | None
    first_name: str
    family_name: str
