from typing import Callable, TypeVar, overload, NoReturn, cast
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.error import MissingMandatoryValueError, UserCancelled, FieldValidationError

class Unset:
    __slots__ = ()

UNSET = Unset()
T = TypeVar("T")

class BaseMenu:

    __PROMPT_INDENT = 1
    _menu_options: list
    _menu_name: str
    

    def __init__(self, session, key_bindings, conn):
        self._session = session
        self._key_bindings = key_bindings
        self._conn = conn

    def _prompt_until_valid(
            self,
            *,
            prompt_text: str,
            getter: Callable[[UserPrompt], T],
            field: str,
            required: bool = False,
            none_option: bool = False,
            is_picklist: bool = False,
            options: list[tuple] | None = None,
            default_value = None
    ) -> T | None:
        
        while True:
            try:                
                prompt = UserPrompt(
                    session = self._session,
                    prompt = self._indent_string(prompt_text + " ", self.__PROMPT_INDENT),
                    none_option = none_option,
                    is_picklist = is_picklist,
                    options = options or [],
                    key_bindings = self._key_bindings,
                    default_value = default_value
                )

                if prompt.is_cancelled:
                    raise UserCancelled()

                value = getter(prompt)

                if required and value is None:
                    raise FieldValidationError(field=field, message="This is a required field.")

                return value

            except (ValueError) as e:
                raise FieldValidationError(field=field, message=str(e))
        
    def _prompt_delete_confirmation(self) -> None:
        
        prompt_message = self._indent_string("Are you sure you want to delete this record?" + " ", self.__PROMPT_INDENT)

        confirm = UserPrompt(
            session = self._session,
            is_picklist = True,
            prompt = prompt_message,
            options = [("no", "no"),("yes", "yes")],
            key_bindings = self._key_bindings
        )

        # Treat a "no" response as a user cancellation
        if confirm.is_cancelled or confirm.get_str() == "no":
            raise UserCancelled()

    def _required(self, value: T | None | Unset, field: str) -> T:
        if value is UNSET or value is None:
            raise MissingMandatoryValueError(f"Missing {field}.")
        return cast(T, value)

    def _optional(self, value: T | None | Unset) -> T | None:
        if value is UNSET:
            return None
        return cast(T, value)

    def _format_title(self, title: str, borders: bool = True, width: int = 60) -> str:
        line = "(" + title.center(width) + ")"
        if borders:
            border = " " + "=" * width + " "
            return f"\n{border}\n{line}\n{border}\n"
        return f"\n{line}\n"
    
    def _retry_message(self, e):
        return self._indent_string(str(e) + " Please try again (or hit CTRL-C to cancel).", 3)

    def _indent_string(self, string: str, spaces: int) -> str:
        return " " * spaces + string
    
    def _format_results_text(self, result_count: int, results: str) -> str:
        indents = ' ' * 5
        if result_count == 0:
            return(f"\n{indents}No matching results.")
        elif result_count == 1:
            return(f"\n{indents}1 match found:\n{results}")
        else:
            return(f"\n{indents}{result_count} matches found:\n{results}")