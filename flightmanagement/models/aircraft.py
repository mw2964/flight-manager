from typing import Optional

class Aircraft:

    def __init__(
        self,
        id: Optional[int] = None,
        registration: Optional[str] = None,
        manufacturer_serial_no: Optional[int] = None,
        icao_hex: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        icao_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> None:
        
        self.__id: Optional[int] = id
        self.__registration: Optional[str] = registration
        self.__manufacturer_serial_no: Optional[int] = manufacturer_serial_no
        self.__icao_hex: Optional[str] = icao_hex
        self.__manufacturer: Optional[str] = manufacturer
        self.__model: Optional[str] = model
        self.__icao_type: Optional[str] = icao_type
        self.__status: Optional[str] = status
    
    # Getters and setters

    @property
    def id(self) -> Optional[int]:
        return self.__id

    @id.setter
    def id(self, value: Optional[int]) -> None:
        if value is not None and value < 0:
            raise ValueError("id must be a non-negative integer or None.")
        self.__id = value
    
    @property
    def registration(self) -> Optional[str]:
        return self.__registration

    @registration.setter
    def registration(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("registration must be a non-empty string.")
        self.__registration = value

    @property
    def manufacturer_serial_no(self) -> Optional[int]:
        return self.__manufacturer_serial_no

    @manufacturer_serial_no.setter
    def manufacturer_serial_no(self, value: Optional[int]) -> None:
        if value is not None and value < 0:
            raise ValueError("manufacturer_serial_no must be a non-negative integer or None.")
        self.__manufacturer_serial_no = value

    @property
    def icao_hex(self) -> Optional[str]:
        return self.__icao_hex

    @icao_hex.setter
    def icao_hex(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("icao_hex must be a non-empty string.")
        self.__icao_hex = value

    @property
    def manufacturer(self) -> Optional[str]:
        return self.__manufacturer

    @manufacturer.setter
    def manufacturer(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("manufacturer must be a non-empty string.")
        self.__manufacturer = value

    @property
    def model(self) -> Optional[str]:
        return self.__model

    @model.setter
    def model(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("model must be a non-empty string.")
        self.__model = value

    @property
    def icao_type(self) -> Optional[str]:
        return self.__icao_type

    @icao_type.setter
    def icao_type(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("icao_type must be a non-empty string.")
        self.__icao_type = value

    @property
    def status(self) -> Optional[str]:
        return self.__status

    @status.setter
    def status(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("status must be a non-empty string.")
        self.__status = value
    
    def __str__(self):
        return self.__registration if self.__registration is not None else str(self)