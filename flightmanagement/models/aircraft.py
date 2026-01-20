from dataclasses import dataclass

@dataclass(frozen=True)
class Aircraft:    
    registration: str    
    manufacturer: str
    model: str    
    status: str = "Active"

    id: int | None = None
    manufacturer_serial_no: int | None = None
    icao_hex: str | None = None
    icao_type: str | None = None

    def __post_init__(self):
        if not self.registration:
            raise ValueError("Invalid registration")
        
        if not self.manufacturer:
            raise ValueError("Invalid manufacturer")
        
        if not self.model:
            raise ValueError("Invalid model")
        
        if not self.status or self.status not in ["Active", "Inactive", "Decommissioned"]:
            raise ValueError("Invalid status")

    def __str__(self):
        return f"{self.registration} ({self.manufacturer} {self.model})"
