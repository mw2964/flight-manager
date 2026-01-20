from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Pilot:    
    first_name: str
    family_name: str

    id: int | None = None

    def __post_init__(self):
        if not self.__is_valid_name(self.first_name):
            raise ValueError("Invalid first name")
        
        if not self.__is_valid_name(self.family_name):
            raise ValueError("Invalid family name")

    def __is_valid_name(self, name: str | None) -> bool:
        if name and re.fullmatch(r"[A-Za-z\s-]+", name):
            return True
        return False

    def __str__(self):
        return f"{self.first_name} {self.family_name}"