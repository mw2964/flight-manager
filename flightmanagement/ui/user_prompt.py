from datetime import datetime
from prompt_toolkit.shortcuts import choice
from flightmanagement.ui.ui_utils import indent_string

class UserPrompt:

    __PROMPT_INDENT = 1
    __MESSAGE_INDENT = 3

    value: str = ""
    is_valid: bool = False
    is_cancelled: bool = False
    validation_error: str = ""

    def __init__(self, session, prompt_type: str, prompt: str, allow_blank: bool = True, options: list[tuple] = [], default_value = None, key_bindings = None):
        self.__session = session
        self.__prompt_type = prompt_type
        self.__prompt = prompt
        self.__allow_blank = allow_blank
        self.__options = options
        self.__default_value = default_value
        self.__key_bindings = key_bindings

        match self.__prompt_type:
            case "text":
                while not self.is_valid and not self.is_cancelled:
                    self.prompt_string()
                    if not self.is_valid and not self.is_cancelled:
                        print(indent_string(self.validation_error, self.__MESSAGE_INDENT))
            case "date":
                while not self.is_valid and not self.is_cancelled:
                    self.prompt_date()
                    if not self.is_valid and not self.is_cancelled:
                        print(indent_string(self.validation_error, self.__MESSAGE_INDENT))
            case "time":
                while not self.is_valid and not self.is_cancelled:
                    self.prompt_time()
                    if not self.is_valid and not self.is_cancelled:
                        print(indent_string(self.validation_error, self.__MESSAGE_INDENT))
            case "integer":
                while not self.is_valid and not self.is_cancelled:
                    self.prompt_integer()
                    if not self.is_valid and not self.is_cancelled:
                        print(indent_string(self.validation_error, self.__MESSAGE_INDENT))
            case "choice":
                if len(self.__options) == 0:
                    raise ValueError("Missing choice options")
                if self.__key_bindings is None:
                    raise ValueError("Missing key bindings for choice list")
                self.prompt_choice()                
            case _:
                raise ValueError("Unknown data type")

    def prompt_choice(self):
        selection = choice(
            message=self.__prompt,
            options=self.__options,
            key_bindings=self.__key_bindings,
            default=self.__default_value
        )
        if selection == "__CANCEL__":
            self.is_cancelled = True
            return
        
        self.value = selection

    def prompt_string(self):
        
        return_value = self.prompt_or_cancel()
        if self.is_cancelled:            
            return
        elif self.is_valid == False:
            if return_value == "":
                self.validation_error = "Value cannot be blank - please try again."
            else:
                self.validation_error = "Invalid value - please try again."
            return
       
        self.is_valid = True
        if return_value is not None:
            self.value = return_value

    def prompt_date(self):

        return_value = self.prompt_or_cancel()
        if self.is_cancelled:            
            return
        elif self.is_valid == False:            
            self.validation_error = "Date cannot be blank - please try again."
            return

        if return_value == "":
            self.value = return_value
            return

        try:
            date = datetime.strptime(return_value, "%d/%m/%Y") # type: ignore
        except ValueError:
            self.is_valid = False
            self.validation_error = "Invalid date - please try again."
            return
        
        self.is_valid = True
        if return_value is not None:
            self.value = datetime.strftime(date, "%Y-%m-%d")

    def prompt_time(self):

        return_value = self.prompt_or_cancel()
        if self.is_cancelled:            
            return
        elif self.is_valid == False:  
            self.validation_error = "Time cannot be blank - please try again."
            return

        if return_value == "":
            self.value = return_value
            return
        
        try:
            time = datetime.strptime(return_value, "%H:%M") # type: ignore
        except ValueError:
            self.is_valid = False
            self.validation_error = "Invalid time - please try again."
            return
        
        self.is_valid = True
        if return_value is not None:
            self.value = return_value
    
    def prompt_integer(self):

        if self.__default_value:
            self.__default_value = str(self.__default_value)

        return_value = self.prompt_or_cancel()
        if self.is_cancelled:            
            return
        elif self.is_valid == False:  
            self.validation_error = "Value cannot be blank - please try again."
            return

        if return_value == "":
            self.value = return_value
            return
        
        try:
            int_value = int(return_value) # type: ignore
        except ValueError:
            self.is_valid = False
            self.validation_error = "Invalid number - please try again."
            return
        
        self.is_valid = True
        if return_value is not None:
            self.value = return_value

    def prompt_or_cancel(self):
    
        indented_message = indent_string(self.__prompt, self.__PROMPT_INDENT)

        if self.__default_value:
            result = self.__session.prompt(
                message=indented_message,
                default=self.__default_value
            )
        else:
            result = self.__session.prompt(
                message=indented_message
            )

        if result == "__CANCEL__":
            self.is_cancelled = True
            return None

        if result == "" and self.__allow_blank == False:
            self.is_valid = False
            return None

        self.is_valid = True
        return result