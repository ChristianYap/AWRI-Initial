#################################################################################
# Name: Christian Yap
# Description: Lincoln Peterson with Chapman's Estimator Program:
# Estimates population using the Lincoln Peterson Chapman Estimator, as well as
# allowing users to change assumed assumptions and parameters and get a simulation.
# Version: 1.0, Created August 2019
#################################################################################
import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
from MainWindow import Ui_MainWindow
import numpy as np
import random
import matplotlib.pyplot as plt


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
        self.GroupButtons()
        self.Connections()
        self.show()

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
        self.captureProbabilityOption.addButton(self.checkBoxCaptureRandomPerSample, 3)
        self.captureProbabilityOption.addButton(self.checkBoxCaptureRandomPerFish, 4)

        # Group Three: Sub-reach Size

        self.subReachSizeOption.addButton(self.checkBoxNormalSubreach, 1)
        self.subReachSizeOption.addButton(self.checkBoxExpandedSubreach, 2)

    #################################################################################
    # Connections for the button click
    #################################################################################
    def Connections(self):
        self.estimatePopulationButton.clicked.connect(self.EstimatePopulationChapman)
        self.runSimulationButton.clicked.connect(self.simulateFishes)

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
            msg.setInformativeText("Amount of recaptured-marked fishes must be less than marked fishes from first catch")
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
        # Equal probability for all fishes and each sample:
        if self.checkBoxCaptureEqual.isChecked():
            captureProbabilityFish = self.captureProbabilityInput.value()
            captureProbabilityType = "Equal Capture Probability for all samples."

    #################################################################################
    # Get Fish population parameter as to whether it is an open or closed population.
    #################################################################################
    def getTagLossParameter(self):
        global tagLossVar
        global tagLossType
        # Equal probability for all fishes and each sample:
        if self.checkBoxNoTagLoss.isChecked():
            # do nothing
            tagLossVar = self.tagLossProbabilityInput.value()
            tagLossType = "No Tag Loss"
        else:
            tagLossVar = self.tagLossProbabilityInput.value()

    #################################################################################
    # Get SubReach Parameter and see if it is normal sized or extended.
    #################################################################################
    def getSubReachSizeParameter(self):
        global subReachSize
        global subReachType
        # SubReach Type
        if self.checkBoxNormalSubreach.isChecked():
            # do nothing
            subReachSize = 0
            subReachType = "Normal Subreach size"
        else:
            subReachSize = 1
            subReachType = "Extended Subreach size"

    #################################################################################
    # Get SubReach Parameter and see if it is normal sized or extended.
    #################################################################################
    def getNumTrials(self):
        global numTrials
        numTrials = self.numTrialsInput.value()

    #################################################################################
    # Simulation and then plot histogram
    #################################################################################
    def simulateAndPlot(self):

        np.random.seed(1000)
        # np_hist = [0, 1, 2, 3]
        np_hist = np.random.normal(loc=0, scale=1, size=1000)
        np_hist[:10]
        np_hist.mean(), np_hist.std()
        hist, bin_edges = np.histogram(np_hist)
        bin_edges = np.round(bin_edges, 0)
        plt.figure(figsize=[10, 8])
        plt.bar(bin_edges[:-1], hist, width=0.5, color='#0504aa', alpha=0.7)
        plt.xlim(min(bin_edges), max(bin_edges))
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value', fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.title('Simulation Histogram', fontsize=15)
        plt.show()
        #https://www.datacamp.com/community/tutorials/histograms-matplotlib

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
        self.simulateAndPlot

        # Print out Parameters
        self.simulationParameterPrint.append("Population Size: " + str(populationSize) + "\tType: " + populationType)
        self.simulationParameterPrint.append("Capture Probability: q = " + str(captureProbabilityFish) + "\tType: "
                                             + captureProbabilityType)
        self.simulationParameterPrint.append(tagLossType + "\t\tSubreach Type: " + subReachType)
        self.simulationParameterPrint.append("Number of Trials: " + str(numTrials))


#################################################################################
# MAIN FUNCTION
#################################################################################
if __name__ == "__main__":
    app = QApplication([])
    ui = MainWindow()
    sys.exit(app.exec_())