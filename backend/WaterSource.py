from backend._common import ChoiceEnum

class WaterSource:
    INSTANCE = None

    def __init__(self):
        WaterSource.INSTANCE = self

        self.year_water = 8
        self.poisoned = False

    #manager acqua villaggio A
    def get_water_villageA(self, choice):
        match choice:
            case ChoiceEnum.SHARED:
                return self.year_water/2
            case ChoiceEnum.ALL_TO_A:
                return self.year_water
            case _:
                return 0

    #manager acqua villaggio B
    def get_water_villageB(self, choice):
        match choice:
            case ChoiceEnum.SHARED:
                return  self.year_water/2
            case ChoiceEnum.ALL_TO_B:
                return self.year_water
            case _:
                return 0
