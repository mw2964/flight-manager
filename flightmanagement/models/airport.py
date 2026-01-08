from typing import Optional

class Airport:

    def __init__(
        self,
        id: Optional[int] = None,
        code: Optional[str] = None,
        name: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None
    ) -> None:
        
        self.__id: Optional[int] = id
        self.__code: Optional[str] = code
        self.__name: Optional[str] = name
        self.__city: Optional[str] = city
        self.__country: Optional[str] = country
        self.__region: Optional[str] = region

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
    def code(self) -> Optional[str]:
        return self.__code

    @code.setter
    def code(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("code must be a non-empty string.")
        self.__code = value

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("name must be a non-empty string.")
        self.__name = value

    @property
    def city(self) -> Optional[str]:
        return self.__city

    @city.setter
    def city(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("city must be a non-empty string.")
        self.__city = value

    @property
    def country(self) -> Optional[str]:
        return self.__country

    @country.setter
    def country(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("country must be a non-empty string.")
        self.__country = value

    @property
    def region(self) -> Optional[str]:
        return self.__region

    @region.setter
    def region(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("region must be a non-empty string.")
        self.__region = value
    
    def __str__(self):
        return self.code if self.code is not None else str(self)