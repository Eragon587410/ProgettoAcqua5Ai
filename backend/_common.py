from enum import Enum

class ChoiceEnum(str, Enum):
    ALL_TO_A = "all to a"
    ALL_TO_B = "all to b"
    SHARED   = "shared"
# #endclass