from backend import TimeLapse



class GlobalManager:
    INSTANCE = None

    def __init__(self, year):
        GlobalManager.INSTANCE = self

        self.choice = None
        self.time   = TimeLapse(year)
    # #enddef

    def set_choice(self, choice):
        self.choice = choice
    # #enddef

    def year_flow(self):
        self.time.year_flow(self.choice)
    # #enddef
# #enclass