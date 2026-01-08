from typing import Optional

class Pilot:

    def __init__(
        self,
        id: Optional[int] = None,
        first_name: Optional[str] = None,
        family_name: Optional[str] = None
    ) -> None:
        
        self.__id: Optional[int] = id
        self.__first_name: Optional[str] = first_name
        self.__family_name: Optional[str] = family_name

    @property
    def id(self) -> Optional[int]:
        return self.__id

    @id.setter
    def id(self, value: Optional[int]) -> None:
        if value is not None and value < 0:
            raise ValueError("id must be a non-negative integer or None.")
        self.__id = value
    
    @property
    def first_name(self) -> Optional[str]:
        return self.__first_name
    
    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("first_name must be a non-empty string.")
        self.__first_name = value
    
    @property
    def family_name(self) -> Optional[str]:
        return self.__family_name
    
    @family_name.setter
    def family_name(self, value: Optional[str]) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("family_name must be a non-empty string.")
        self.__family_name = value
    
    def __str__(self) -> str:
        return f"{self.id}. {self.first_name} {self.family_name}"