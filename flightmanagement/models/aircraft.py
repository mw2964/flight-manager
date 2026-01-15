from dataclasses import dataclass

@dataclass
class Aircraft:
        id: int | None
        registration: str
        manufacturer_serial_no: int | None
        icao_hex: str | None
        manufacturer: str
        model: str
        icao_type: str | None
        status: str
