from enum import Enum

class TextColours(Enum):
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def colourstring(text, colour):
    return TextColours[colour].value + str(text) + TextColours.RESET.value