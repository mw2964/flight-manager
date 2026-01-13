from datetime import datetime

def prompt_or_cancel(session, message: str, cancel_message: str, default_value = None):
    
    indented_message = indent_string(message, 5)

    if default_value:
        result = session.prompt(
            message=indented_message,
            default=default_value
        )
    else:
        result = session.prompt(
            message=indented_message
        )

    if result == "__CANCEL__":
        print(f"\n{cancel_message}")
        return None
    return result

def indent_string(string: str, spaces: int) -> str:
    return " " * spaces + string

def prompt_date(session, prompt: str, allow_blank: bool, default=None) -> str | None:

    if default:
        value = prompt_or_cancel(session, prompt, "Update cancelled", default)
    else:
        value = prompt_or_cancel(session, prompt, "Update cancelled")

    if not value:
        if allow_blank:
            return None        
        raise ValueError("Invalid date")

    try:
        date = datetime.strptime(value, "%d/%m/%Y")
    except:
        raise ValueError("Invalid date")
    
    return datetime.strftime(date, "%Y-%m-%d")

def prompt_time(session, prompt: str, allow_blank: bool, default=None) -> str | None:

    if default:
        value = prompt_or_cancel(session, prompt, "Update cancelled", default)
    else:
        value = prompt_or_cancel(session, prompt, "Update cancelled")

    if not value:
        if allow_blank:
            return None        
        raise ValueError("Invalid time")

    try:
        date = datetime.strptime(value, "%H:%M")
    except:
        raise ValueError("Invalid time")
    
    return datetime.strftime(date, "%H:%M")
