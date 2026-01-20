from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Airport:
    code: str
    
    id: int | None = None
    name: str | None = None
    city: str | None = None
    country: str | None = None
    region: str | None = None

    def __post_init__(self):
        if not self.__is_valid_code(self.code):
            raise ValueError("Invalid code")

    def __is_valid_code(self, code: str | None) -> bool:
        if code and re.fullmatch(r"^[A-Z][A-Z][A-Z]$", code):
            return True
        return False

    def __str__(self):
        return f"{self.code} ({self.name})"