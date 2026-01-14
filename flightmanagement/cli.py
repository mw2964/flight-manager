from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from flightmanagement.ui.main_menu import MainMenu

CANCEL = "__CANCEL__"

bindings = KeyBindings()

@bindings.add('c-c')
def _(event):
    event.app.exit(result=CANCEL)            

session = PromptSession(key_bindings=bindings)

print("\n***********\nFLIGHT CLUB\nV0.1\n***********")

try:
    MainMenu(session, bindings).load()
except RuntimeError as e:
    print(e)
