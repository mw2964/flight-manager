
class Pilot:

    def __init__(self, id: int, first_name: str, family_name: str) -> None:
        
        self.__id = id
        self.__first_name = first_name
        self.__family_name = family_name

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        if value is not None and value < 0:
            raise ValueError("id must be a non-negative integer or None.")
        self.__id = value
    
    @property
    def first_name(self) -> str:
        return self.__first_name
    
    @first_name.setter
    def first_name(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("first_name must be a non-empty string.")
        self.__first_name = value
    
    @property
    def family_name(self) -> str:
        return self.__family_name
    
    @family_name.setter
    def family_name(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("family_name must be a non-empty string.")
        self.__family_name = value
    
    def __str__(self) -> str:
        return f"{self.id}. {self.first_name} {self.family_name}"