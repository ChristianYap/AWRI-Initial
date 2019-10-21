#################################################################################
# Simulation Parameters Class
#################################################################################
from copy import copy, deepcopy

from Fish import Fish
from SimulationParameters import SimulationParameters


class TestResults:
    actualPopulation: int
    estimatedPopulation: float
    firstPassFishesCaught: int
    secondPassFishesCaught: int
    secondPassFishesRecaught: int
    fishPop: []

    #################################################################################
    # FISH CONSTRUCTOR
    #################################################################################
    def __init__(self):
        self.estimatedPopulation = 0
        self.firstPassFishesCaught = 0
        self.secondPassFishesCaught = 0
        self.secondPassFishesRecaught = 0

    #################################################################################
    # FISH CONSTRUCTOR
    #################################################################################
    def __init__(self, actualPopulation, estPopulation, firstPassCaught, secondPassCaught, reCaught, fishPop):
        self.actualPopulation = actualPopulation
        self.estimatedPopulation = estPopulation
        self.firstPassFishesCaught = firstPassCaught
        self.secondPassFishesCaught = secondPassCaught
        self.secondPassFishesRecaught = reCaught
        self.fishPop = fishPop

    #################################################################################
    # SETTER FOR ACTUAL POPULATION
    #################################################################################
    def SetActualPopulation(self, actPopulation):
        self.actualPopulation = actPopulation

    #################################################################################
    # SETTER FOR ESTIMATED POPULATION
    #################################################################################
    def SetEstimatedPopulation(self, estimatedPopulation):
        self.estimatedPopulation = estimatedPopulation

    #################################################################################
    # SETTER FOR NUMBER OF FISHES CAUGHT IN FIRST PASS
    #################################################################################
    def SetFirstPassCaught(self,  firstPassFishesCaught):
        self.firstPassFishesCaught = firstPassFishesCaught

    #################################################################################
    # SETTER FOR NUMBER OF FISHES CAUGHT IN SECOND PASS
    #################################################################################
    def SetSecondPassCaught(self,  secondPassFishesCaught):
        self.secondPassFishesCaught = secondPassFishesCaught

    #################################################################################
    # SETTER FOR NUMBER OF FISHES RE-CAUGHT IN SECOND PASS
    #################################################################################
    def SetSecondPassRecaught(self,  secondPassFishesRecaught):
        self.secondPassFishesRecaught = secondPassFishesRecaught

    #################################################################################
    # SETTER FOR FISH DATA IN THIS TRIAL
    #################################################################################
    def SetFishData(self, fishData):
        self.fishData.append(fishData)

    #################################################################################
    # GETTER FOR ESTIMATED POPULATION
    #################################################################################
    def GetActualPopulation(self):
        return self.actualPopulation

    #################################################################################
    # GETTER FOR ESTIMATED POPULATION
    #################################################################################
    def GetEstimatedPopulation(self):
        return self.estimatedPopulation

    #################################################################################
    # GSETTER FOR NUMBER OF FISHES CAUGHT IN FIRST PASS
    #################################################################################
    def GetFirstPassCaught(self):
        return self.firstPassFishesCaught

    #################################################################################
    # GETTER FOR NUMBER OF FISHES CAUGHT IN SECOND PASS
    #################################################################################
    def GetSecondPassCaught(self):
        return self.secondPassFishesCaught

    #################################################################################
    # GETTER FOR NUMBER OF FISHES RE-CAUGHT IN SECOND PASS
    #################################################################################
    def GetSecondPassRecaught(self):
       return self.secondPassFishesRecaught

    #################################################################################
    # GETTER FOR FISH DATA IN THIS TRIAL
    #################################################################################
    def GetFishData(self):
        return self.fishPop


