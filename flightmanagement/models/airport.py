from dataclasses import dataclass

@dataclass
class Airport:
    id: int | None
    code: str
    name: str | None
    city: str | None
    country: str | None
    region: str | None

    def __str__(self):
        return f"{self.code} ({self.name})"