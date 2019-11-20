#################################################################################
# FISH CLASS
# Class to give each fish a personality
#################################################################################


class Fish:
    captureProbQ: float
    captureProbQTwo: float
    tagged: int
    tagLoss: float
    subReachPos: int
    subReachPosTwo: int
    mortality: int
    migrationDistance: int
    reCaught: ''

    #################################################################################
    # FISH CONSTRUCTOR
    #################################################################################
    def __init__(self, captureProbQ: float, tagged: int, tagLoss: float, subReachPos: int, mortality: int,
                 migrationDistance: int):
        self.captureProbQ = captureProbQ
        self.captureProbQTwo = -1
        self.tagged = tagged
        self.tagLoss = tagLoss
        self.subReachPos = subReachPos
        self.subReachPosTwo = -1
        self.mortality = mortality
        self.migrationDistance = migrationDistance
        self.reCaught = '-'

    #################################################################################
    # SETTER FOR FISH TAGGING
    #################################################################################
    def SetCaptureProbability(self, captureProbQ):
        self.captureProbQ = captureProbQ

    #################################################################################
    # SETTER FOR FISH TAGGING
    #################################################################################
    def SetCaptureProbabilityTwo(self, captureProbQTwo):
        self.captureProbQTwo = captureProbQTwo

    #################################################################################
    # SETTER FOR FISH TAGGING
    #################################################################################
    def SetFishTag(self, tagStatus):
        self.tagged = tagStatus

    #################################################################################
    # SETTER FOR TAG LOSS
    #################################################################################
    def SetTagLoss(self, tagLoss):
        self.tagLoss = tagLoss

    #################################################################################
    # SETTER SUBREACH POSITION OF THE FISH
    #################################################################################
    def SetSubReachPos(self, zone):
        self.subReachPos = zone

    #################################################################################
    # SETTER SUBREACH POSITION TWO OF THE FISH
    #################################################################################
    def SetSubReachPosTwo(self, zone):
        self.subReachPosTwo = zone

    def SetMigrationDistance(self, distance):
        self.migrationDistance = distance

    #################################################################################
    # SETTER FOR MORTALITY: 1 FISH IS ALIVE, 0 IT'S DEAD
    #################################################################################
    def SetMortality(self, mortality):
        self.mortality = mortality

    #################################################################################
    # SETTER FOR RECAUGHT STATUS
    #################################################################################
    def SetRecaughtStat(self, reCaught):
        self.reCaught = reCaught

    #################################################################################
    # GETTER FOR FISH  Q 1
    #################################################################################
    def GetCaptureProbability(self):
        return self.captureProbQ

    #################################################################################
    # GETTER FOR FISH Q 2
    #################################################################################
    def GetCaptureProbabilityTwo(self):
        return self.captureProbQTwo

    #################################################################################
    # GETTER FOR FISH TAGGING
    #################################################################################
    def GetFishTag(self):
        return self.tagged

    #################################################################################
    # GETTER FOR TAG LOSS
    #################################################################################
    def GetTagLoss(self):
        return self.tagLoss

    #################################################################################
    # GETTER SUBREACH POSITION OF THE FISH
    #################################################################################
    def GetSubReachPos(self):
        return self.subReachPos

    #################################################################################
    # SETTER SUBREACH POSITION TWO OF THE FISH
    #################################################################################
    def GetSubReachPosTwo(self):
        return self.subReachPosTwo

    #################################################################################
    # SETTER FOR MORTALITY: 1 FISH IS ALIVE, 0 IT'S DEAD
    #################################################################################
    def GetMortality(self):
        return self.mortality

    #################################################################################
    # Get whether fish is entering or leaving or staying.
    #################################################################################
    def GetMigrationDistance(self):
        return self.migrationDistance

    #################################################################################
    # GETTER FOR RECAUGHT STATUS
    #################################################################################
    def GetRecaughtStat(self):
        return self.reCaught
