from datetime import datetime, date, time
from prompt_toolkit.shortcuts import choice
from flightmanagement.error import InvalidDateError, InvalidFloatError, InvalidIntegerError, InvalidTimeError

class UserPrompt:
    """
    This class provides a unified interface for collecting and validating user input
    in the command-line UI. It provides both free-text prompts and selectable
    picklists, optional default values, and cancellation handling.

    Raw user input is stored as a string and exposes helper methods to
    convert and validate the value as common data types (string, date, time,
    integer, float), raising domain-specific validation errors when input is invalid.
    """

    __string_value: str | None = None

    is_valid: bool = False
    is_cancelled: bool = False
    validation_error: str = ""

    def __init__(
            self,
            session,
            prompt: str,
            is_picklist: bool = False,
            options: list[tuple] = [],
            none_option: bool = False,
            default_value = None,
            key_bindings = None
        ):
        self.__session = session
        self.__prompt = prompt
        self.__none_option = none_option
        self.__options = options
        self.__default_value = default_value
        self.__key_bindings = key_bindings

        if is_picklist:
            self._get_choice()
        else:
            self._get_prompt()

    def _get_choice(self):
        """
        Provide a selectable picklist of options.
        
        Input may be received in different formats, but is stored in string format.
        """

        if self.__none_option and self.__options is not None:
            self.__options.insert(0, (-1, "None"))
            
        selection = choice(
            message = self.__prompt + "\n",
            options = self.__options,
            key_bindings = self.__key_bindings,
            default = self.__default_value
        )
        if selection == "__CANCEL__":
            self.is_cancelled = True
            return
        
        if selection != -1:
            self.__string_value = str(selection)

    def _get_prompt(self):
        """
        Provide free-text prompt.
        
        Input is received and stored in string format.
        """

        if self.__default_value:
            result = self.__session.prompt(
                message = self.__prompt,
                default = str(self.__default_value)
            )
        else:
            result = self.__session.prompt(
                message = self.__prompt
            )

        if result == "__CANCEL__":
            self.is_cancelled = True
            return

        self.__string_value = str(result).strip() if result else None

    def get_str(self) -> str | None:
        """
        Return the input value in string format.
        """

        return self.__string_value

    def get_date(self) -> date | None:
        """
        Validate the input value as a date, and return as a date type.

        If the input is not in a valid '%d/%m/%Y' format, raise a ValueError.
        """

        if self.__string_value is None:
            return None
        try:
            return datetime.strptime(self.__string_value, "%d/%m/%Y")
        except ValueError as e:
            raise InvalidDateError("The date must be in DD/MM/YYYY format.")

    def get_time(self) -> time | None:
        """
        Validate the input value as a time, and return as a time type.

        If the input cannot be converted into a valid time, raise a ValueError.
        """

        if self.__string_value is None:
            return None
        try:
            return time.fromisoformat(self.__string_value)
        except ValueError as e:
            raise InvalidTimeError("The time must be HH:MM format.")

    def get_int(self) -> int | None:
        """
        Validate the input value as an integer, and return as an int type.

        If the input cannot be converted into an int, raise a ValueError.
        """
                
        if self.__string_value is None:
            return None
        try:
            return int(self.__string_value)
        except ValueError as e:
            raise InvalidIntegerError("The value must be an integer.")

    def get_float(self) -> float | None:
        """
        Validate the input value as float, and return as an float type.

        If the input cannot be converted into a float, raise a ValueError.
        """

        if self.__string_value is None:
            return None
        try:
            return float(self.__string_value)
        except ValueError as e:
            raise InvalidFloatError("The value must be numeric.")
