from aiogram.fsm.state import StatesGroup, State

class RegistrationForm(StatesGroup):
    name = State()
    forename = State()
    group = State()
    sex = State()

def check_registration_state(state):
    return RegistrationForm.name.state == state or \
           RegistrationForm.forename.state == state or \
           RegistrationForm.group.state == state or \
           RegistrationForm.sex.state == state