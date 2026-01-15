from dataclasses import dataclass

@dataclass
class Pilot:
    id: int | None
    first_name: str
    family_name: str

    def __str__(self):
        return f"{self.first_name} {self.family_name}"