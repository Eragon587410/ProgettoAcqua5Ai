from backend.TimeLapse import TimeLapse
from backend._common import ChoiceEnum
from backend.Village import Village

import random



class GlobalManager:
    INSTANCE = None
    VILLAGE_SOLDIERS = 40

    def __init__(self, year):
        GlobalManager.INSTANCE = self

        self.choice = None
        self.time   = TimeLapse(year)
    # #enddef

    def set_choice(self, choice):
        if (self.choice == ChoiceEnum.ALL_TO_A or self.choice == ChoiceEnum.ALL_TO_B) and choice == ChoiceEnum.SHARED:
            if self.choice == ChoiceEnum.ALL_TO_A:
                Village.VILLAGGIO_A.riserva_acqua -= 30
                Village.VILLAGGIO_B.modifica_riserva_acqua(30)
            else:
                Village.VILLAGGIO_B.riserva_acqua -= 30
                Village.VILLAGGIO_A.modifica_riserva_acqua(30)
        self.choice = choice
    # #enddef

    def year_flow(self):
        self.time.year_flow(self.choice)
    # #enddef
# #enclass

    def war(self):
        winner = None

        soldier_a = min(Village.VILLAGGIO_A.num_persone, GlobalManager.VILLAGE_SOLDIERS)
        soldier_b = min(Village.VILLAGGIO_B.num_persone, GlobalManager.VILLAGE_SOLDIERS)

        if abs(soldier_a - soldier_b) > 10:
            winner = "A" if soldier_a > soldier_b else "B"
        else:
            value = random.randint(1, 2)
            winner = "A" if value == 1 else "B"


        if winner == "A":
            Village.VILLAGGIO_A.num_persone -=  int(soldier_a/100*random.randint(40, 80))
            Village.VILLAGGIO_B.num_persone -= soldier_b
            self.choice = ChoiceEnum.ALL_TO_A
            Village.VILLAGGIO_A.morale += 10
            Village.VILLAGGIO_A.morale -= 10
        else:
            Village.VILLAGGIO_B.num_persone -=  int(soldier_b/100*random.randint(40, 80))
            Village.VILLAGGIO_A.num_persone -= soldier_a
            self.choice = ChoiceEnum.ALL_TO_B
            Village.VILLAGGIO_B.morale += 10
            Village.VILLAGGIO_A.morale -= 10

        return winner

        