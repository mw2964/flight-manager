from dataclasses import dataclass

@dataclass
class Airport:
    id: int
    code: str
    name: str | None
    city: str | None
    country: str | None
    region: str | None
