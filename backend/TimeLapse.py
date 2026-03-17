from backend import Village
from backend import WaterSource

class TimeLapse:

    def __init__(self, year):
        self.year = year
    # #enddef

    def year_flow(self, choice):
        Village.VILLAGGIO_A.aggiorna_anno(WaterSource.INSTANCE.get_water_villageA(choice))
        Village.VILLAGGIO_B.aggiorna_anno(WaterSource.INSTANCE.get_water_villageB(choice))
        self.year += 1
    # #enddef

# #endclass