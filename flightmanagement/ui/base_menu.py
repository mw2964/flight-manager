from typing import Callable, TypeVar, overload, NoReturn, cast
from flightmanagement.ui.user_prompt import UserPrompt
from flightmanagement.error import MissingMandatoryValueError, UserCancelled, FieldValidationError

class Unset:
    __slots__ = ()

UNSET = Unset()
T = TypeVar("T")

class BaseMenu:
    """
    This class provides shared functionality for interactive CLI menus within the
    application. It centralises common behaviours such as prompting users for input,
    validating required and optional fields, handling cancellations, and formatting
    menu output.

    The class builds on UserPrompt to repeatedly request input until valid data is
    supplied, converts prompt results into strongly typed values, and raises
    domain-specific exceptions for validation errors or user-initiated cancellations.
    It also includes helper methods for confirmation prompts, title and result
    formatting, and consistent text indentation across menus.
    """

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
        """
        Prompt the user for input until a valid value is provided or the user cancels.

        This method displays either a free-text prompt or a picklist prompt using
        UserPrompt, applies the supplied getter to extract and validate the value,
        and enforces required-field constraints.

        Args:
            prompt_text: The text displayed to the user.
            getter: A function that extracts and validates a typed value from
                a UserPrompt instance.
            field: The logical field name, used for validation error messages.
            required: Whether the field must have a value.
            none_option: Whether to include a selectable 'None' option.
            is_picklist: Whether the prompt should be a picklist rather than free text.
            options: Picklist options as (value, label) tuples.
            default_value: Default value shown in the prompt, if any.

        Returns:
            The validated value, or None if the field is optional and no value is supplied.

        Raises:
            UserCancelled: If the user cancels the prompt.
            FieldValidationError: If the input fails validation.
        """

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

            except ValueError as e:
                raise FieldValidationError(field=field, message=str(e))
        
    def _prompt_delete_confirmation(self) -> None:
        """
        Prompt the user to confirm deletion of a record.

        Displays a yes/no picklist confirmation prompt. Any cancellation or
        explicit 'no' response is treated as a user cancellation.

        Raises:
            UserCancelled: If the user cancels or selects 'no'.
        """
        
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
        """
        Enforce that a value is present for a required field.

        Args:
            value: The value to validate.
            field: The field name used in the error message.

        Returns:
            The validated value.

        Raises:
            MissingMandatoryValueError: If the value is missing or unset.
        """

        if value is UNSET or value is None:
            raise MissingMandatoryValueError(f"Missing {field}.")
        return cast(T, value)

    def _optional(self, value: T | None | Unset) -> T | None:
        """
        Normalize an optional field value.

        Converts UNSET values to None while preserving explicitly provided values.

        Args:
            value: The value to normalize.

        Returns:
            The normalized value or None.
        """

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
        return self._indent_string(str(e) + " Please try again (or hit CTRL-C to cancel).\n", 3)

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