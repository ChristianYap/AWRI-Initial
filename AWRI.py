#################################################################################
# Name: Christian Yap
# Description: Lincoln Peterson with Chapman's Estimator Program:
# Estimates population using the Lincoln Peterson Chapman Estimator, as well as
# allowing users to change assumed assumptions and parameters and get a simulation.
# Version: 1.0, Created August 2019
#################################################################################
import sys
import random
from copy import deepcopy

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
from MainWindow import Ui_MainWindow
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from SimulationParameters import SimulationParameters
from Fish import Fish
from TestResults import TestResults

# Global Variables
simulationSaves = []


#################################################################################
# CLASS FOR THE GUI
#################################################################################
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        # Declare the user interface:
        super(MainWindow, self).__init__(*args, **kwargs)

        # Create Button Groups
        self.populationOption = QButtonGroup()
        self.captureProbabilityOption = QButtonGroup()
        self.subReachSizeOption = QButtonGroup()

        # Build the user interface
        self.setupUi(self)

        # Insert buttons to their respective groups
        self.Presets()
        self.GroupButtons()
        self.Connections()
        self.show()

    #################################################################################
    # Update UI Presets
    #################################################################################
    def Presets(self):
        self.openPopulationMoralityInput.setVisible(False)
        self.mortalityProbabilityTitle.setVisible(False)
        self.saveResultsButton.setEnabled(False)

    #################################################################################
    # Group the buttons so user can only choose one option in each group
    #################################################################################
    def GroupButtons(self):
        # Group one: Closed / Open Population
        self.populationOption.addButton(self.checkBoxClosedPopulation, 1)
        self.populationOption.addButton(self.checkBoxOpenPopulation, 2)
        self.populationOption.setExclusive(True)

        # Group two: Capture Probability
        self.captureProbabilityOption.addButton(self.checkBoxCaptureEqual, 1)
        self.captureProbabilityOption.addButton(self.checkBoxCaptureVary, 2)
        self.captureProbabilityOption.addButton(self.checkBoxCaptureRandomPerFish, 3)

        # Group Three: Sub-reach Size
        self.subReachSizeOption.addButton(self.checkBoxNoSubreach, 1)
        self.subReachSizeOption.addButton(self.checkBoxNormalSubreach, 2)
        self.subReachSizeOption.addButton(self.checkBoxExpandedSubreach, 3)

    #################################################################################
    # Connections for the button click
    #################################################################################
    def Connections(self):
        self.estimatePopulationButton.clicked.connect(self.EstimatePopulationChapman)
        self.runSimulationButton.clicked.connect(self.simulateFishes)

        # Toggle checkbox connections:
        # Population
        self.checkBoxClosedPopulation.stateChanged.connect(self.checkBoxPopulationOption)
        self.checkBoxOpenPopulation.stateChanged.connect(self.checkBoxPopulationOption)

        # Capture Probability
        self.checkBoxCaptureEqual.stateChanged.connect(self.checkBoxProbabilityOption)
        self.checkBoxCaptureVary.stateChanged.connect(self.checkBoxProbabilityOption)
        self.checkBoxCaptureRandomPerFish.stateChanged.connect(self.checkBoxProbabilityOption)

        # Tag Loss
        self.checkBoxTagLoss.stateChanged.connect(self.CheckBoxTagLossOption)

        # Refresh Results Button
        self.refreshResultsButton.clicked.connect(self.RefreshResults)

        # Save Results Button
        self.saveResultsButton.clicked.connect(self.SaveResults)

    #################################################################################
    # Save Results
    #################################################################################
    def SaveResults(self):
        plt.savefig('test.png')

    #################################################################################
    # Open or Closed Population
    #################################################################################
    def checkBoxPopulationOption(self):
        if self.checkBoxClosedPopulation.isChecked():
            self.openPopulationMoralityInput.setVisible(False)
            self.mortalityProbabilityTitle.setVisible(False)
        else:
            self.openPopulationMoralityInput.setVisible(True)
            self.mortalityProbabilityTitle.setVisible(True)

    #################################################################################
    # Capture Probability Options
    #################################################################################
    def checkBoxProbabilityOption(self):
        if self.checkBoxCaptureEqual.isChecked():
            self.captureProbabilityInput.setEnabled(True)
            self.captureProbabilityInputVaryTwo.setEnabled(False)
        elif self.checkBoxCaptureVary.isChecked():
            self.captureProbabilityInput.setEnabled(True)
            self.captureProbabilityInputVaryTwo.setEnabled(True)
        elif self.checkBoxCaptureRandomPerFish.isChecked():
            self.captureProbabilityInput.setEnabled(False)
            self.captureProbabilityInputVaryTwo.setEnabled(False)

    #################################################################################
    # Tag Loss Enable Disable
    #################################################################################
    def CheckBoxTagLossOption(self):
        if self.checkBoxTagLoss.isChecked():
            self.tagLossProbabilityInput.setEnabled(True)
        else:
            self.tagLossProbabilityInput.setEnabled(False)

    #################################################################################
    # Refresh results button
    #################################################################################
    def RefreshResults(self):
        # test
        inputNumber = self.loadSimulationNumberInput.value() - 1
        template = simulationSaves[0]

        # View Simulation Parameters
        self.simulationReviewer.append('Mean Population estimated: ' + str(template.GetOverallEstimatedPopulation()))
        self.simulationReviewer.append('Actual Population size: ' + str(template.GetActualEstimatedPopulation()))
        self.simulationReviewer.append('Number of Trials:' + str(template.GetNumTrials()))
        self.simulationReviewer.append(template.GetParameters())

        # View Trial Results

        # View Fish Data for each trial

        # Graph

    #################################################################################
    # Lincoln Peterson Calculation
    #################################################################################
    def LincolnPetersonChapmanFormula(self):

        markFirstCatchM = int(self.markedFirstCatchInput.value())
        captureSecondCatchC = int(self.caughtSecondCatchInput.value())
        markSecondCatchR = int(self.markedSecondCatchInput.value())

        # Error Check: Marked second fishes cannot be greater than Marked First Fishes
        if markSecondCatchR > markFirstCatchM:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Invalid Input:")
            msg.setInformativeText(
                "Amount of recaptured-marked fishes must be less than marked fishes from first catch")
            msg.setWindowTitle("Error")
            msg.exec_()

        # Error Check: Marked second fishes cannot be greater than Captured Second Fishes
        elif markSecondCatchR > captureSecondCatchC:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Invalid Input:")
            msg.setInformativeText("Number of marked fishes in second catch cannot be greater than number of "
                                   "recaptured fish")
            msg.setWindowTitle("Error")
            msg.exec_()

        # Else we are good:
        else:
            estimatedSampleSizeN = (((markFirstCatchM + 1) * (captureSecondCatchC + 1)) / (markSecondCatchR + 1)) - 1
            # Date and Time set:
            dateNow = QTime.currentTime().toString()
            self.resultScreenOne.append(dateNow + " - Estimated Fish Population: " + str(estimatedSampleSizeN))
            # QMessageBox.information(self, "A Good Message", "Success. Results shown in the results box.")

    #################################################################################
    # Estimate Population using Lincoln Peterson's Chapman Model - TAB ONE
    #################################################################################
    def EstimatePopulationChapman(self):
        self.LincolnPetersonChapmanFormula()

    #################################################################################
    # Get Fish population parameter as to whether it is an open or closed population.
    #################################################################################
    def getPopulationParameter(self):
        global populationSize
        global populationType
        if self.checkBoxClosedPopulation.isChecked():
            populationSize = self.totalPopulationInput.value()
            populationType = "Closed Population"
        elif self.checkBoxOpenPopulation.isChecked():
            populationSize = self.totalPopulationInput.value()
            populationType = "Open Population"

    #################################################################################
    # Get Capture Probability for the fishes and/or the sample
    #################################################################################
    def getCaptureProbabilityParameter(self):
        global captureProbabilityFish
        global captureProbabilityType
        global captureProbabilityString
        # Equal probability for all fishes and each sample:
        if self.checkBoxCaptureEqual.isChecked():
            captureProbabilityFish = self.captureProbabilityInput.value()
            captureProbabilityString = 'Capture Probability q = ' + str(captureProbabilityFish)
            captureProbabilityType = "Equal Capture Probability for all samples."
        if self.checkBoxCaptureVary.isChecked():
            captureProbabilityFish = self.captureProbabilityInput.value()
            captureProbabilityFishTwo = self.captureProbabilityInputVaryTwo.value()
            captureProbabilityString = 'Capture Probability for First Pass: q = ' + str(captureProbabilityFish) \
                                       + 'Capture Probability for Second Pass: q = ' + str(captureProbabilityFishTwo)
            captureProbabilityType = "Capture Probability Varying Per Sample."
        if self.checkBoxCaptureRandomPerFish.isChecked():
            captureProbabilityString = 'CaptureProbability: Completely Random'
            captureProbabilityType = "Capture Probability Completely Random per Fish."

    #################################################################################
    # Get Fish population parameter as to whether it is an open or closed population.
    #################################################################################
    def getTagLossParameter(self):
        global tagLossVar
        global tagLossType
        # Equal probability for all fishes and each sample:
        if not self.checkBoxTagLoss.isChecked():
            # do nothing
            tagLossVar = self.tagLossProbabilityInput.value()
            tagLossType = "No Tag Loss"
        else:
            tagLossVar = self.tagLossProbabilityInput.value()
            tagLossType = "Possible tag loss at " + str(tagLossVar * 100) + "%"

    #################################################################################
    # Get SubReach Parameter and see if it is normal sized or extended.
    #################################################################################
    def getSubReachSizeParameter(self):
        global subReachSize
        global subReachType

        # SubReach Type
        if self.checkBoxNoSubreach.isChecked():
            # All fishes are fair game to get caught
            subReachSize = 0
            subReachType = "No Subreach Parameter"
        elif self.checkBoxNormalSubreach.isChecked():
            # Divided into 4 (0 to 3) Subreach zones, fishes in Zone 1 and 2 can be caught:
            subReachSize = 1
            subReachType = "Normal Subreach Size"
        elif self.checkBoxExpandedSubreach.isChecked():
            # Divided into 6 (0 to 5) Subreach zones, fishes in zone 1,2,3 can be caught:
            subReachSize = 6
            subreachType = "Expanded Subreach Size"

    #################################################################################
    # Get SubReach Parameter and see if it is normal sized or extended.
    #################################################################################
    def getNumTrials(self):
        global numTrials
        numTrials = self.numTrialsInput.value()

    #################################################################################
    # Function  for graphing given an array value
    #################################################################################
    def graphingStuff(self, arrayValue):
        count, bins, ignored = plt.hist(arrayValue, 4, facecolor='green')
        plt.xlabel('Binomial Distribution (n = 1, p = 0.5')
        plt.ylabel('Count')
        plt.title("Binomial Distribution Histogram (Bin size 4)")
        plt.axis([0, 1, 0, 1000])  # x_start, x_end, y_start, y_end
        plt.grid(True)
        plt.show(block=False)
        # https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.binomial.html
        # https://www.differencebetween.com/difference-between-bernoulli-and-vs-binomial/
        # https://stackoverflow.com/questions/47012474/bernoulli-random-number-generator
        # https://stackoverflow.com/questions/22744577/plotting-basic-uniform-distribution-on-python

    #################################################################################
    # Simulate Fishes
    #################################################################################
    def simulate(self, simulationResults):

        # Be able to save data for each simulation:
        for i in range(0, numTrials):
            # Generate random numbers
            qCatchValue = np.random.rand(populationSize)
            tagLossIndex = []
            # self.graphingStuff(tagLossValue)

            # ####################### Create fish structure, generate characteristics for each fish ############### #
            for m in range(len(qCatchValue)):
                if m == 0:
                    fish = Fish(qCatchValue[m], -1, -1, -1, 1, -1)
                    fishPopulation = [fish]
                    # print(str(fishPopulation[i].captureProbQ))
                else:
                    fish = Fish(qCatchValue[m], -1, -1, -1, 1, -1)
                    fishPopulation.insert(m, fish)
                    # print(str(fishPopulation[i].captureProbQ))

                # FIX DO ARRAY INSTEAD. Designate first locations of the fish:
                if self.checkBoxNormalSubreach.isChecked():
                    # Fishes in range 0 and 3 are out of reach.
                    fishPopulation[m].SetSubReachPos(random.randrange(4))
                elif self.checkBoxExpandedSubreach.isChecked():
                    # Fishes in range 0 and 5 are out of reach.
                    fishPopulation[m].SetSubReachPos(random.randrange(6))

            # ################################START THE FIRST PASS ################################################# #

            firstPassMarkedFishes = 0
            # First set of fish population marked.
            for j in range(len(qCatchValue)):
                # If subreach is not a factor:
                if self.checkBoxNoSubreach.isChecked():
                    # Do the first scenario if there is equal or varying probability between samples:
                    if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                        if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                            # Tag the fish
                            fishPopulation[j].SetFishTag(1)
                            tagLossIndex.append(j)
                            # Increment Counter:
                            firstPassMarkedFishes += 1
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                            # Tag the fish
                            fishPopulation[j].SetFishTag(1)
                            tagLossIndex.append(j)
                            # Increment Counter:
                            firstPassMarkedFishes += 1
                    # End this scenario
                # End the no sub reach parameter
                # If sub reach is normal, meaning 4 zones, Zone 0 and 3 are out of bones. 1 and 2 are catachable.
                elif self.checkBoxNormalSubreach.isChecked():
                    # Do the first scenario if there is equal or varying probability between samples:
                    if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                        # Capture only if the fish is in the subreach (zone 1 and 2):
                        if fishPopulation[j].GetSubReachPos() == '1' or fishPopulation[j].GetSubReachPos() == '2':
                            if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if fishPopulation[j].GetSubReachPos() == '1' or fishPopulation[j].GetSubReachPos() == '2':
                            if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                    # End this scenario
                # End the normal sub reach parameter
                # If sub reach is extended, meaning 6 zones, Zone 0 and 5 are out of bounds 1, 2, 3, 4 are catchachable.
                elif self.checkBoxExpandedSubreach.isChecked():
                    # Do the first scenario if there is equal or varying probability between samples:
                    if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                        # Capture only if the fish is in the subreach (zone 1, 2, 3, 4):
                        if fishPopulation[j].GetSubReachPos() == '1' or fishPopulation[j].GetSubReachPos() == '2' or \
                                fishPopulation[j].GetSubReachPos() == '3' or fishPopulation[j].GetSubReachPos() == '4':
                            # Let's try to capture the fish
                            if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if fishPopulation[j].GetSubReachPos() == '1' or fishPopulation[j].GetSubReachPos() == '2' or \
                                fishPopulation[j].GetSubReachPos() == '3' or fishPopulation[j].GetSubReachPos() == '4':
                            # Let's try to capture the fish
                            if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                    # End this scenario
                # End the extended reach parameter

            # ############################################## BREAK ################################################# #
            # Tag loss scenario:
            tagLossCounter = 0
            # See if the fish loses its tag after being tagged.
            if self.checkBoxTagLoss.isChecked():
                tagLossValue = np.random.rand(len(tagLossIndex))
                for v in range(len(tagLossIndex)):
                    fishPopulation[v].SetTagLoss(tagLossValue[v])
                    if fishPopulation[v].tagLoss <= tagLossVar:
                        fishPopulation[j].SetFishTag(0)
                        tagLossCounter += 1

            # ########################################### END BREAK ################################################# #

            # self.simulationParameterPrint.append('Fishes caught during first pass: ' + str(firstPassMarkedFishes))
            # ################################ START SECOND PASS ################################################# #
            # Create new catch values
            qCatchValueTwo = np.random.rand(populationSize)
            fishDeath = np.random.rand(populationSize)

            # Declare variables
            secondPassFishes = 0
            recapturedTaggedFish = 0

            # SECOND CAPTURE
            for k in range(len(qCatchValueTwo)):
                fishPopulation[k].SetCaptureProbability(qCatchValueTwo[k])

                # Designate second location of the fish:
                if self.checkBoxNormalSubreach.isChecked():
                    # Fishes in range 0 and 3 are out of reach.
                    fishPopulation[k].SetSubReachPosTwo(random.randrange(4))
                elif self.checkBoxExpandedSubreach.isChecked():
                    # Fishes in range 0 and 5 are out of reach.
                    fishPopulation[k].SetSubReachPosTwo(random.randrange(6))

                # Mortality an option?
                if self.checkBoxOpenPopulation.isChecked():
                    if fishDeath[k] <= self.openPopulationMoralityInput.value():
                        # Kill the fish:
                        fishPopulation[k].SetMortality(0)

                # First scenario: no sub reach parameter:
                if self.checkBoxNoSubreach.isChecked():
                    # Do this first scenario if there is equal probability between the two samples:
                    if self.checkBoxCaptureEqual.isChecked():
                        if fishPopulation[k].captureProbQ <= self.captureProbabilityInput.value():
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                    # Do this second scenario if sample two has different capture variability from first capture sample:
                    elif self.checkBoxCaptureVary.isChecked():
                        if fishPopulation[k].captureProbQ <= self.captureProbabilityInputVaryTwo.value():
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                    # Do this third scenario if fish has random capture probability as well:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if fishPopulation[k].captureProbQ <= randomCaptureProbabilityRoll[0]:
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                # Second scenario: normal sub reach parameter:
                elif self.checkBoxNormalSubreach.isChecked():
                    # Do this first scenario if there is equal probability between the two samples:
                    if self.checkBoxCaptureEqual.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if fishPopulation[k].GetSubReachPosTwo() == '1' or fishPopulation[k].GetSubReachPosTwo() == '2':
                            # Can we capture it?
                            if fishPopulation[k].captureProbQ <= self.captureProbabilityInput.value():
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                    # Do this second scenario if sample two has different capture variability from first capture sample:
                    elif self.checkBoxCaptureVary.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if fishPopulation[k].GetSubReachPosTwo() == '1' or fishPopulation[k].GetSubReachPosTwo() == '2':
                            # Can we capture it?
                            if fishPopulation[k].captureProbQ <= self.captureProbabilityInputVaryTwo.value():
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                    # Do this third scenario if fish has random capture probability as well:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if fishPopulation[k].GetSubReachPosTwo() == '1' or fishPopulation[k].GetSubReachPosTwo() == '2':
                            # Can we capture it?
                            randomCaptureProbabilityRoll = np.random.rand(1)
                            if fishPopulation[k].captureProbQ <= randomCaptureProbabilityRoll[0]:
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                # Third scenario: expanded sub reach parameter:
                elif self.checkBoxExpandedSubreach.isChecked():
                    # Do this first scenario if there is equal probability between the two samples:
                    if self.checkBoxCaptureEqual.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if fishPopulation[k].GetSubReachPosTwo() == '1' or fishPopulation[
                            k].GetSubReachPosTwo() == '2' or \
                                fishPopulation[k].GetSubReachPosTwo() == '3' or fishPopulation[
                            k].GetSubReachPosTwo() == '4':
                            # Can we capture it?
                            if fishPopulation[k].captureProbQ <= self.captureProbabilityInput.value():
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                    # Do this second scenario if sample two has different capture variability from first capture sample:
                    elif self.checkBoxCaptureVary.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if fishPopulation[k].GetSubReachPosTwo() == '1' or fishPopulation[
                            k].GetSubReachPosTwo() == '2' or \
                                fishPopulation[k].GetSubReachPosTwo() == '3' or fishPopulation[
                            k].GetSubReachPosTwo() == '4':
                            # Can we capture it?
                            if fishPopulation[k].captureProbQ <= self.captureProbabilityInputVaryTwo.value():
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                    # Do this third scenario if fish has random capture probability as well:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if fishPopulation[k].GetSubReachPosTwo() == '1' or fishPopulation[
                            k].GetSubReachPosTwo() == '2' or \
                                fishPopulation[k].GetSubReachPosTwo() == '3' or fishPopulation[
                            k].GetSubReachPosTwo() == '4':
                            # Can we capture it?
                            randomCaptureProbabilityRoll = np.random.rand(1)
                            if fishPopulation[k].captureProbQ <= randomCaptureProbabilityRoll[0]:
                                secondPassFishes += 1
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
            # End Second Capture Pass

            # Estimation formula
            estimatedSampleSizeN = (((firstPassMarkedFishes + 1) * (secondPassFishes + 1)) / (
                    recapturedTaggedFish + 1)) - 1

            simulationResults.append(estimatedSampleSizeN)

            # ######## START RAW DATA SAVING, ALLOWS USER TO VIEW RESULTS OF EACH SIMULATION ######################### #

            # Put this test result in a list for raw  data viewing:
            if i == 0:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes,
                                         recapturedTaggedFish, fishPopulation)
                testResultsArray = [testResult]
            else:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes,
                                         recapturedTaggedFish, fishPopulation)
                testResultsArray.insert(i, testResult)

        # TODO: TEST FISH POPULATION THING IN TEST RESULTS1!!
        x = testResult.GetFishData()
        print(str(x[0].GetCaptureProbability()))

        # Add the overall summary for this result to the saved array for all simulations
        thisSimulation = SimulationParameters(numTrials, estimatedSampleSizeN, populationSize, testResultsArray)
        thisSimulation.SetParameterString(populationType + "\n" + captureProbabilityString + "\n" \
                                          + captureProbabilityType + "\n" + tagLossType + "\n" + subReachType)
        simulationSaves.append(thisSimulation)

    #################################################################################
    # Simulation and then plot histogram
    #################################################################################
    def simulateAndPlot(self):

        # Declare array for results:
        simulationResults = []

        self.simulationParameterPrint.clear()
        self.simulate(simulationResults)
        arrayResult = np.array(simulationResults)
        # End for loop

        self.simulationParameterPrint.append('Mean Population estimation: ' + str(arrayResult.mean()))
        # Print out Parameters
        self.simulationParameterPrint.append(
            "Actual Population Size: " + str(populationSize) + "\tType: " + populationType)
        self.simulationParameterPrint.append(captureProbabilityString + "\tType: "
                                             + captureProbabilityType)
        self.simulationParameterPrint.append(tagLossType + "\t\tSubreach Type: " + subReachType)
        self.simulationParameterPrint.append("Number of Trials: " + str(numTrials))

        # Graph
        # count number in each bin
        bins = np.linspace(min(simulationResults), max(simulationResults))
        hist, _ = np.histogram(simulationResults, bins)
        plt.figure(figsize=[10, 8])
        # plt.bar(bin_edges[:-1], hist, width=0.5, color='#0504aa', alpha=0.7)
        plt.bar(bins[:-1], hist, label=str(populationSize) + ' samples', width=1)
        # plt.plot(bins[:-1], hist, 'r-', lw=5)
        plt.axvline(populationSize, color='g', linestyle="dashed", lw=2, label=str('True Population Size'))
        plt.axvline(arrayResult.mean(), color='r', lw=2, label=str('Simulation Mean'))
        plt.xlim(min(bins), max(bins))
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Population Estimate', fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.title('Population Estimate Simulation N = ' + str(numTrials), fontsize=15)
        plt.legend(loc='best')
        plt.show()
        # https://www.datacamp.com/community/tutorials/histograms-matplotlib
        # https://www.youtube.com/watch?time_continue=79&v=Z2zUGmqIDto

    #################################################################################
    # SIMULATION - TAB TWO
    #################################################################################
    def simulateFishes(self):

        # QMessageBox.information(self, "A Good Message", "Success. Results shown in the results box.")

        # Get Population and whether it is a closed population or open population
        self.getPopulationParameter()
        # Get Capture Probability for the Samples
        self.getCaptureProbabilityParameter()
        # Get Tag Loss True/False
        self.getTagLossParameter()
        # Get SubReach Size
        self.getSubReachSizeParameter()
        # Get Number of Trials
        self.getNumTrials()
        # Simulate and plot
        self.simulateAndPlot()
        # Enable Save Button
        self.saveResultsButton.setEnabled(True)
        self.refreshResultsButton.setEnabled(True)


#################################################################################
# MAIN FUNCTION
#################################################################################
if __name__ == "__main__":
    app = QApplication([])
    ui = MainWindow()
    sys.exit(app.exec_())
