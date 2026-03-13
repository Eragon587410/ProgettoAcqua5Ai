class WaterSource:
    INSTANCE: WaterSource

    def __init__(self):
        WaterSource.INSTANCE = self

        self.year_water = 4

    #manager acqua villaggio A
    def get_water_villageA(self):
        if GlobalManager.INSTANCE.choice == ChoiceEnum.SHARED:
            return self.year_water/2
        elif GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_A:
            return self.year_water
        else:
            return 0

    #manager acqua villaggio B
    def get_water_villageB(self):
        if GlobalManager.INSTANCE.choice == ChoiceEnum.SHARED:
            return  self.year_water/2
        elif GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_B:
            return self.year_water
        else:
            return 0
