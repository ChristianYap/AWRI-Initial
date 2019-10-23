#################################################################################
# Simulation Parameters Class
#################################################################################
from Fish import Fish


class SimulationParameters:
    parameters: str
    numberTrials: int
    estimatedPopulation: float
    actualPopulation: int
    testData = []

    #################################################################################
    # FISH CONSTRUCTOR
    #################################################################################
    def __init__(self):
        self.numberTrials = -1
        self.estimatedPopulation = -1
        self.actualPopulation = -1
        self.parameters = ''

    #################################################################################
    # FISH CONSTRUCTOR
    #################################################################################
    def __init__(self, numberTrials: int, estimatedPopulation: float, actualPopulation: int,
                 testData):
        # Trial results:
        self.numberTrials = numberTrials
        self.estimatedPopulation = estimatedPopulation
        self.actualPopulation = actualPopulation
        self.testData = testData
        self.parameters = ''

    #################################################################################
    # SETTER FOR STRING
    #################################################################################
    def SetParameterString(self, addText):
        self.parameters = self.parameters + addText

    #################################################################################
    # SETTER FOR NUMBER OF TRIALS RAN
    #################################################################################
    def SetNumTrials(self, numTrials):
        self.numberTrials = numTrials

    #################################################################################
    # SETTER FOR OVERALL FISH POPULATION ESTIMATED
    #################################################################################
    def SetOverallEstimatedPopulation(self, estimatedPopulation):
        self.estimatedPopulation = estimatedPopulation

    #################################################################################
    # SETTER FOR ACTUAL FISH POPULATION
    #################################################################################
    def SetActualEstimatedPopulation(self, actualPopulation):
        self.actualPopulation = actualPopulation

    #################################################################################
    # SETTER FOR TEST DATA FOR THIS SIMULATION
    #################################################################################
    def SetActualEstimatedPopulation(self, testData):
        self.testData = testData

    #################################################################################
    # GETTER FOR NUMBER OF TRIALS DONE
    #################################################################################
    def GetNumTrials(self):
        return self.numberTrials

    #################################################################################
    # GETTER FOR NUMBER OF TRIALS DONE
    #################################################################################
    def GetOverallEstimatedPopulation(self):
        return self.estimatedPopulation

    #################################################################################
    # GETTER FOR ACTUAL POPULATION
    #################################################################################
    def GetActualPopulation(self):
        return self.actualPopulation

    #################################################################################
    # GETTER FOR NUMBER OF TRIALS DONE
    #################################################################################
    def GetNumTrials(self):
        return self.numberTrials

    #################################################################################
    # GETTER FOR TEST DATA
    #################################################################################
    def GetParameters(self):
        return self.parameters

    #################################################################################
    # GETTER FOR TEST DATA
    #################################################################################
    def GetTestData(self):
        return self.testData
