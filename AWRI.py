#################################################################################
# Name: Christian Yap
# Description: Lincoln Peterson with Chapman's Estimator Program:
# Estimates population using the Lincoln Peterson Chapman Estimator, as well as
# allowing users to change assumed assumptions and parameters and get a simulation.
# Version: 1.0, Created August 2019
#################################################################################
import random
import sys
import os
import csv
import time
import traceback
import concurrent.futures

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from MainWindow import Ui_MainWindow
import numpy as np
import matplotlib.pyplot as plt
from SimulationParameters import SimulationParameters
from Fish import Fish
from TestResults import TestResults
from scipy.stats import beta

# Global Variables
REACH_SIZE = 100
BETA_DISTRIBUTION = 2.75
simulationSaves = []
global simulationResult


#################################################################################
# CLASS FOR WORKER SIGNALS
#################################################################################
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


#################################################################################
# CLASS FOR QRunnable
#################################################################################
class Worker(QRunnable):
    '''
        Worker thread

        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

        :param callback: The function callback to run on this worker thread. Supplied args and
                         kwargs will be passed through to the runner.
        :type callback: function
        :param args: Arguments to pass to the callback function
        :param kwargs: Keywords to pass to the callback function

        '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            resultThread = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(resultThread)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


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

        # Allow for threading
        self.threadpool = QThreadPool()
        print("Multi-threading with maximum %d threads" % self.threadpool.maxThreadCount())

    #################################################################################
    # Update UI Presets
    #################################################################################
    def Presets(self):
        self.openPopulationMoralityInput.setVisible(False)

        self.migrationDistanceBox.setVisible(False)
        self.migrationDistanceSlider.setVisible(False)
        self.migrationDistanceTitle.setVisible(False)
        self.migrationRateDescription.setVisible(False)
        self.migrationRateBox.setVisible(False)
        self.migrationRateSlider.setVisible(False)
        self.migrationRateTitle.setVisible(False)
        self.checkBoxShowDistribution.setVisible(False)

        self.subReachMovementOption.setEnabled(False)
        self.subReachMovementOption.setVisible(False)
        self.subReachMovementOptionBox.setEnabled(False)
        self.subReachMovementOptionBox.setVisible(False)

        self.mortalityProbabilityTitle.setVisible(False)
        self.saveResultsButton.setEnabled(False)
        self.clearDataButton.setEnabled(False)
        self.loadSimulationNumberInput.setCurrentText('1')

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
        self.subReachSizeOption.addButton(self.checkBoxVariedSubreach, 2)

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

        # Slider
        self.migrationRateSlider.valueChanged.connect(self.MigrationSlider)
        self.migrationDistanceSlider.valueChanged.connect(self.MigrationDistanceSlider)
        self.subReachMovementOption.valueChanged.connect(self.SubreachSizeSlider)

        # Capture Probability
        self.checkBoxCaptureEqual.stateChanged.connect(self.checkBoxProbabilityOption)
        self.checkBoxCaptureVary.stateChanged.connect(self.checkBoxProbabilityOption)
        self.checkBoxCaptureRandomPerFish.stateChanged.connect(self.checkBoxProbabilityOption)

        # Tag Loss
        self.checkBoxTagLoss.stateChanged.connect(self.CheckBoxTagLossOption)

        # View image button
        self.viewImageButton.clicked.connect(self.ViewImage)

        # Refresh Results Button
        self.tableRawTestData.clicked.connect(self.DisplayFishData)
        self.tableRawFishData.doubleClicked.connect(self.DisplayAnalysisForColumn)
        self.refreshResultsButton.clicked.connect(self.RefreshResults)
        self.clearDataButton.clicked.connect(self.ClearSavedData)

        # Subreach Options
        self.checkBoxNoSubreach.stateChanged.connect(self.SubReachOption)
        self.checkBoxVariedSubreach.stateChanged.connect(self.SubReachOption)

        # Save Results Button
        self.saveResultsButton.clicked.connect(self.SaveResults)

    #################################################################################
    # Clear Saved Data
    #################################################################################
    def ClearSavedData(self):
        simulationSaves.clear()
        self.clearDataButton.setEnabled(False)
        self.refreshResultsButton.setEnabled(False)
        self.viewImageButton.setEnabled(False)
        self.loadSimulationNumberInput.clear()
        self.tableRawTestData.setRowCount(0)
        self.tableRawFishData.setRowCount(0)
        self.simulationReviewer.clear()

    #################################################################################
    # Subreach Size Slider
    #################################################################################
    def SubreachSizeSlider(self):
        self.subReachMovementOptionBox.setValue(self.subReachMovementOption.value() / 100)

    #################################################################################
    # Migration Rate (SKEWED DOWNSTREAM, BALANCED, UPSTREAM) slide
    #################################################################################
    def MigrationSlider(self):
        global migrationBiasVal
        global migrationBiasStatus

        self.migrationRateBox.setValue(self.migrationRateSlider.value() / 100)
        migrationBiasVal = self.migrationRateSlider.value() / 100

        if self.migrationRateBox.value() <= -0.5:
            self.migrationRateDescription.setText('Downstream Bias')
        elif 0 <= self.migrationRateBox.value() <= -0.25:
            self.migrationRateDescription.setText('Slight Downstream Bias')
        elif self.migrationRateBox.value() == 0:
            self.migrationRateDescription.setText('Balanced')
        elif 0.50 <= self.migrationRateBox.value() < 0.25:
            self.migrationRateDescription.setText('Slight Upstream Bias')
        elif self.migrationRateBox.value() >= 0.5:
            self.migrationRateDescription.setText('Upstream Bias')

        migrationBiasStatus = self.migrationRateDescription.text() + ': ' + str(migrationBiasVal)

        if self.checkBoxShowDistribution.isChecked():
            correction = self.migrationRateBox.value() - 0.5
            # https://www.geeksforgeeks.org/scipy-stats-beta-python/
            betaX = np.linspace(0, 1, 100)
            y1 = beta.pdf(betaX, BETA_DISTRIBUTION, BETA_DISTRIBUTION)
            plt.plot(betaX + correction, y1 + REACH_SIZE * self.migrationDistanceBox.value() - (BETA_DISTRIBUTION / 2), "*")
            plt.show()

        #################################################################################

    # Migration Distance (0 - 100 - 200 % ) of subreach slide:
    #################################################################################
    def MigrationDistanceSlider(self):
        global migrationDistVal
        global migrationDistStatus

        self.migrationDistanceBox.setValue(self.migrationDistanceSlider.value() / 100)
        migrationDistVal = self.migrationDistanceSlider.value() / 100
        migrationDistStatus = 'Migration Distance: ' + str(migrationDistVal)

    #################################################################################
    # Subreach Options
    #################################################################################
    def SubReachOption(self):
        if self.checkBoxNoSubreach.isChecked():
            self.subReachMovementOption.setVisible(False)
            self.subReachMovementOption.setEnabled(False)
            self.subReachMovementOptionBox.setEnabled(False)
            self.subReachMovementOptionBox.setVisible(False)
        elif self.checkBoxVariedSubreach.isChecked():
            self.subReachMovementOption.setEnabled(True)
            self.subReachMovementOption.setVisible(True)
            self.subReachMovementOptionBox.setEnabled(True)
            self.subReachMovementOptionBox.setVisible(True)

    #################################################################################
    # Display Population Analysis
    #################################################################################
    def DisplayPopulationAnalysis(self):
        # Choose column to graph:
        index = self.tableRawFishData.currentColumn()

        # Get input number
        inputNumber = int(self.loadSimulationNumberInput.currentText()) - 1
        # View Trial Results:
        testResults = simulationSaves[inputNumber].GetTestData()
        simulationResults = []
        # Get row and column highlighted:
        for idx in range(self.tableRawTestData.rowCount()):
            # Get fish data for that specific test:
            fishData = testResults[idx].GetFishData()
            # Show fish data:
            if index == 0:
                # CAPTURE PROB Q1
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetCaptureProbability())
            elif index == 1:
                # Sub reach S1
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetSubReachPos())
            elif index == 2:
                # Tagged
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetFishTag())
            elif index == 3:
                # Tag Lost
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetTagLoss())
            elif index == 4:
                # Mortality
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetMortality())
            elif index == 5:
                # Enter stay exit
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetMigrationDistance())
            elif index == 6:
                # CAPTURE PROB Q2
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetCaptureProbabilityTwo())
            elif index == 7:
                # FINAL Subreach S2
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetSubReachPosTwo())

        arrayResult = np.array(simulationResults)

        n, bins, patches = plt.hist(x=arrayResult, bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value')
        plt.ylabel('Frequency')

        if index == 0:
            # CAPTURE PROB Q1
            plt.title('Capture Probability Q1 (1st Pass)')
        elif index == 1:
            # subreach S1
            plt.title('Subreach Position S1 (1st Pass)')
        elif index == 2:
            # Tagged
            plt.title('Fishes Tagged')
        elif index == 3:
            # Tag Loss
            plt.title('Tag Loss Spread')
        elif index == 4:
            # Mortality
            plt.title('Mortality Spread')
        elif index == 5:
            # Enter stay exit
            plt.title('Migration Distance Spread')
        elif index == 6:
            # CAPTURE PROB Q2
            plt.title('Capture Probability Q2 (2nd Pass)')
        elif index == 7:
            # FINAL Subreach S2
            plt.title('Subreach Position 2 Spread')

        plt.text(23, 45, r'$\mu=15, b=3$')
        maxFreq = n.max()
        # Set a clean upper y-axis limit.
        plt.ylim(ymax=np.ceil(maxFreq / 10) * 10 if maxFreq % 10 else maxFreq + 10)
        # plt.bar(np.arange(len(arrayResult)), arrayResult)
        plt.show()

    #################################################################################
    # Analyze spread for a column chosen in raw fish data table
    #################################################################################
    def DisplayAnalysisForColumn(self):

        if self.populationGraphCheckBox.isChecked():
            plt.close()
            self.DisplayPopulationAnalysis()
        else:
            plt.close()
            index = self.tableRawFishData.currentColumn()

            # Get input number
            inputNumber = int(self.loadSimulationNumberInput.currentText()) - 1

            # View Trial Results:
            testResults = simulationSaves[inputNumber].GetTestData()

            # Get row and column highlighted:
            for idx in self.tableRawTestData.selectionModel().selectedIndexes():
                rowNum = idx.row()

            # Get fish data for that specific test:
            fishData = testResults[rowNum].GetFishData()
            simulationResults = []
            # Show fish data:
            if index == 0:
                # CAPTURE PROB Q1
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetCaptureProbability())
            elif index == 1:
                # subreach S1
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetSubReachPos())
            elif index == 2:
                # Tagged
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetFishTag())
            elif index == 3:
                # Tag Lost
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetTagLoss())
            elif index == 4:
                # Mortality
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetMortality())
            elif index == 5:
                # Enter stay exit
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetMigrationDistance())
            elif index == 6:
                # CAPTURE PROB Q2
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetCaptureProbabilityTwo())
            elif index == 7:
                # FINAL Subreach S2
                for itr in range(0, len(fishData)):
                    simulationResults.append(fishData[itr].GetSubReachPosTwo())

            arrayResult = np.array(simulationResults)

            n, bins, patches = plt.hist(x=arrayResult, bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
            plt.grid(axis='y', alpha=0.75)
            plt.xlabel('Value')
            plt.ylabel('Frequency')

            if index == 0:
                # CAPTURE PROB Q1
                plt.title('Capture Probability Q1 (1st Pass)')
            elif index == 1:
                # subreach S1
                plt.title('Subreach Position S1 (1st Pass)')
            elif index == 2:
                # Tagged
                plt.title('Fishes Tagged')
            elif index == 3:
                # Tag Loss
                plt.title('Tag Loss Spread')
            elif index == 4:
                # Mortality
                plt.title('Mortality Spread')
            elif index == 5:
                # Enter stay exit
                plt.title('Migration Distance Spread')
            elif index == 6:
                # CAPTURE PROB Q2
                plt.title('Capture Probability Q2 (2nd Pass)')
            elif index == 7:
                # FINAL Subreach S2
                plt.title('Subreach Position 2 Spread')

            plt.text(23, 45, r'$\mu=15, b=3$')
            maxFreq = n.max()
            # Set a clean upper y-axis limit.
            plt.ylim(ymax=np.ceil(maxFreq / 10) * 10 if maxFreq % 10 else maxFreq + 10)
            # plt.bar(np.arange(len(arrayResult)), arrayResult)
            plt.show()

    #################################################################################
    # Save Results
    #################################################################################
    def SaveResults(self):
        path = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'), "CSV Files(*.csv)")
        if path[0] != '':
            with open(path[0], 'w') as csv_file:
                print('Saving file...')
                writer = csv.writer(csv_file, dialect='excel', delimiter=',')
                headers = []
                for column in range(self.tableRawFishData.columnCount()):
                    header = self.tableRawFishData.horizontalHeaderItem(column)
                    if header is not None:
                        headers.append(header.text())
                    else:
                        headers.append("Column " + str(column))
                writer.writerow(headers)
                for row in range(self.tableRawFishData.rowCount()):
                    rowdata = []
                    for column in range(self.tableRawFishData.columnCount()):
                        item = self.tableRawFishData.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

    #################################################################################
    # Open or Closed Population
    #################################################################################
    def checkBoxPopulationOption(self):
        if self.checkBoxClosedPopulation.isChecked():
            self.openPopulationMoralityInput.setVisible(False)
            self.mortalityProbabilityTitle.setVisible(False)

            self.migrationDistanceBox.setVisible(False)
            self.migrationDistanceSlider.setVisible(False)
            self.migrationDistanceTitle.setVisible(False)
            self.migrationRateDescription.setVisible(False)

            self.migrationRateBox.setVisible(False)
            self.migrationRateSlider.setVisible(False)
            self.migrationRateTitle.setVisible(False)
            self.checkBoxShowDistribution.setVisible(False)

            self.checkBoxNoSubreach.setEnabled(True)
            self.checkBoxNoSubreach.setChecked(True)
        else:
            self.openPopulationMoralityInput.setVisible(True)
            self.mortalityProbabilityTitle.setVisible(True)

            self.migrationDistanceBox.setVisible(True)
            self.migrationDistanceSlider.setVisible(True)
            self.migrationDistanceTitle.setVisible(True)
            self.migrationRateDescription.setVisible(True)

            self.migrationRateBox.setVisible(True)
            self.migrationRateSlider.setVisible(True)
            self.migrationRateTitle.setVisible(True)
            self.checkBoxShowDistribution.setVisible(True)
            self.checkBoxNoSubreach.setEnabled(False)

            self.checkBoxVariedSubreach.setChecked(True)

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
    # Review Image
    #################################################################################
    def ViewImage(self):

        # Get input number
        inputNumber = int(self.loadSimulationNumberInput.currentText()) - 1
        template = simulationSaves[inputNumber]
        localPopulationSize = template.GetActualPopulation()
        testDataView = template.GetTestData()
        simulationResults = []

        for i in range(len(testDataView)):
            simulationResults.append(testDataView[i].GetEstimatedPopulation())

        bins = np.linspace(min(simulationResults), max(simulationResults))
        hist, _ = np.histogram(simulationResults, bins)
        plt.figure(figsize=[10, 8])
        # plt.bar(bin_edges[:-1], hist, width=0.5, color='#0504aa', alpha=0.7)
        plt.bar(bins[:-1], hist, label=str(template.GetNumTrials()) + ' trials', width=1)
        # plt.plot(bins[:-1], hist, 'r-', lw=5)
        plt.axvline(localPopulationSize, color='g', linestyle="dashed", lw=2, label=str('True Population Size'))
        plt.axvline(template.GetOverallEstimatedPopulation(), color='r', lw=2, label=str('Simulation Mean'))
        plt.xlim(min(bins), max(bins))
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Population Estimate\n Mean Population Estimation = ' + str('{number:.{digits}f}'.format(number=template.GetOverallEstimatedPopulation(), digits=2)),
                   fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.title('Population Estimate Simulation N = ' + str(localPopulationSize), fontsize=15)
        plt.legend(loc='best')
        plt.show()

    #################################################################################
    # Refresh results button
    #################################################################################
    def RefreshResults(self):

        self.tableRawTestData.setSortingEnabled(False)

        # Clear tables:
        self.tableRawTestData.setRowCount(0)
        self.tableRawFishData.setRowCount(0)

        # Error checking for right input:
        if not self.loadSimulationNumberInput.currentText().isdigit():
            self.loadSimulationNumberInput.setCurrentText(str(1))

        # Get input number
        inputNumber = int(self.loadSimulationNumberInput.currentText()) - 1

        # Error Checking for max input Number:
        if inputNumber >= len(simulationSaves):
            inputNumber = len(simulationSaves) - 1
            self.loadSimulationNumberInput.setCurrentText(str(inputNumber + 1))

        template = simulationSaves[inputNumber]

        # View Simulation Parameters:
        self.simulationReviewer.clear()
        self.simulationReviewer.append('Mean Population estimated: ' + str(template.GetOverallEstimatedPopulation()))
        self.simulationReviewer.append('Actual Population size: ' + str(template.GetActualPopulation()))
        self.simulationReviewer.append('Number of Trials:' + str(template.GetNumTrials()))
        self.simulationReviewer.append(template.GetParameters())

        # View Trial Results:
        testResults = simulationSaves[inputNumber].GetTestData()

        # Create a empty row at bottom of table
        for trials in range(0, len(testResults)):
            numRows = self.tableRawTestData.rowCount()
            self.tableRawTestData.insertRow(numRows)
            self.tableRawTestData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=testResults[trials].GetEstimatedPopulation(), digits=4))))
            self.tableRawTestData.setItem(numRows, 1, QTableWidgetItem(str(testResults[trials].GetFirstPassCaught())))
            self.tableRawTestData.setItem(numRows, 2, QTableWidgetItem(str(testResults[trials].GetSecondPassCaught())))
            self.tableRawTestData.setItem(numRows, 3, QTableWidgetItem(str(testResults[trials].GetSecondPassRecaught())))

        self.tableRawTestData.setSortingEnabled(True)

    #################################################################################
    # Lincoln Peterson Calculation
    #################################################################################
    def DisplayFishData(self):

        # Clear table
        self.tableRawFishData.setRowCount(0)
        self.tableRawFishData.setSortingEnabled(False)

        # Get input number
        inputNumber = int(self.loadSimulationNumberInput.currentText()) - 1

        # View Trial Results:
        testResults = simulationSaves[inputNumber].GetTestData()

        # Get row and column highlighted:
        for idx in self.tableRawTestData.selectionModel().selectedIndexes():
            rowNum = idx.row()

        # Get fish data for that specific test:
        fishData = testResults[rowNum].GetFishData()

        # Show fish data:
        for itr in range(0, len(fishData)):
            numRows = self.tableRawFishData.rowCount()

            self.tableRawFishData.insertRow(numRows)
            self.tableRawFishData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbability(), digits=4))))
            self.tableRawFishData.setItem(numRows, 1, QTableWidgetItem(str(fishData[itr].GetSubReachPos())))
            self.tableRawFishData.setItem(numRows, 2, QTableWidgetItem(str(fishData[itr].GetFishTag())))
            self.tableRawFishData.setItem(numRows, 3, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetTagLoss(), digits=4))))
            self.tableRawFishData.setItem(numRows, 4, QTableWidgetItem(str(fishData[itr].GetMortality())))
            self.tableRawFishData.setItem(numRows, 5, QTableWidgetItem(str(fishData[itr].GetMigrationDistance())))
            self.tableRawFishData.setItem(numRows, 6, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbabilityTwo(), digits=4))))
            self.tableRawFishData.setItem(numRows, 7, QTableWidgetItem(str(fishData[itr].GetSubReachPosTwo())))
            self.tableRawFishData.setItem(numRows, 8, QTableWidgetItem(str(fishData[itr].GetRecaughtStat())))

        self.tableRawFishData.setSortingEnabled(True)

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
        global migrationString

        if self.checkBoxClosedPopulation.isChecked():
            populationSize = self.totalPopulationInput.value()
            populationType = "Closed Population"
            migrationString = "Migration Distance/Rate: None"
        elif self.checkBoxOpenPopulation.isChecked():
            populationSize = self.totalPopulationInput.value()
            populationType = "Open Population"
            self.MigrationSlider()
            self.MigrationDistanceSlider()
            migrationString = migrationBiasStatus + migrationDistStatus

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
            subReachType = "No Subreach Parameter"
        elif self.checkBoxVariedSubreach.isChecked():
            subReachType = "Varied Subreach Size"

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

    def SetSubReachBoundary(self):
        global lowerBoundStudyReach
        global upperBoundStudyReach

        size = (REACH_SIZE * self.subReachMovementOptionBox.value())
        lowerBoundStudyReach = (REACH_SIZE / 2) - (size / 2)
        upperBoundStudyReach = (REACH_SIZE / 2) + (size / 2)

    #################################################################################
    # Simulate Fishes
    #################################################################################
    def simulate(self, simulationResults):

        # Be able to save data for each simulation:
        for i in range(0, numTrials):

            # Generate random numbers for capture probability:
            if self.checkBoxClosedPopulation.isChecked():
                qCatchValue = np.random.rand(populationSize)
            elif self.checkBoxOpenPopulation.isChecked():
                qCatchValue = np.random.rand(populationSize * 3)
            tagLossIndex = []
            fishLocation = []

            # For Open Population, do three areas:
            if self.checkBoxOpenPopulation.isChecked():
                # Range size - 100 to 200, [-inf, 0) is out of bounds, [0, 100] is the study reach default, [101, to inf) is out of bounds
                # First 1/3 of area: D (downstream),  Second 1/3 of area: C (central), Third 1/3 of area: U (upstream)
                fishLocation.extend(np.random.randint(-REACH_SIZE, 1, populationSize))
                fishLocation.extend(np.random.randint(1, REACH_SIZE + 1, populationSize))
                fishLocation.extend(np.random.randint(REACH_SIZE + 1, REACH_SIZE * 2, populationSize))
            # Else we do one whole study reach:
            else:
                # Range size: 0 to 100
                fishLocation = [np.random.randint(0, REACH_SIZE + 1) for p in range(0, populationSize)]
                # Set initial location of fish:

            # Get lower and upper bounds
            self.SetSubReachBoundary()

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

                # Set location of the fish:
                fishPopulation[m].SetSubReachPos(fishLocation[m])

            # ################################START THE FIRST PASS ################################################# #
            firstPassMarkedFishes = 0
            # First set of fish population marked.
            for j in range(len(qCatchValue)):
                # ############################# If sub reach is not a factor: ############################# #
                if self.checkBoxNoSubreach.isChecked():
                    # Do the first scenario if there is equal or varying probability between samples:
                    if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                        if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                            # Tag the fish
                            fishPopulation[j].SetFishTag(1)
                            tagLossIndex.append(j)
                            # Increment Counter:
                            firstPassMarkedFishes += 1
                            fishPopulation[j].SetRecaughtStat('FIRST PASS')
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                            # Tag the fish
                            fishPopulation[j].SetFishTag(1)
                            tagLossIndex.append(j)
                            # Increment Counter:
                            firstPassMarkedFishes += 1
                            fishPopulation[j].SetRecaughtStat('FIRST PASS')
                    # End this scenario
                # ############################# End the no sub reach parameter ############################# #
                # If sub reach is a factor, catch only those in study
                elif self.checkBoxVariedSubreach.isChecked():
                    # Do the first scenario if there is equal or varying probability between samples:
                    if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                        # Capture only if the fish is in the range:
                        if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                            if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                                fishPopulation[j].SetRecaughtStat('FIRST PASS')
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                            if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                                fishPopulation[j].SetRecaughtStat('FIRST PASS')
                    # End this scenario
                # End the normal sub reach parameter
            # ############################################## BREAK ################################################# #
            # Tag loss scenario:
            tagLossCounter = 0
            # See if the fish loses its tag after being tagged.
            if self.checkBoxTagLoss.isChecked():
                tagLossValue = np.random.rand(len(tagLossIndex))
                for v in range(len(tagLossIndex)):
                    fishPopulation[tagLossIndex[v]].SetTagLoss(tagLossValue[v])
                    if fishPopulation[tagLossIndex[v]].tagLoss <= tagLossVar:
                        fishPopulation[tagLossIndex[v]].SetFishTag(0)
                        tagLossCounter += 1

            # ########################################### END BREAK ################################################# #
            # self.simulationParameterPrint.append('Fishes caught during first pass: ' + str(firstPassMarkedFishes))
            # ################################ START SECOND PASS ################################################# #
            # Create new catch values
            # Generate random numbers for capture probability:
            if self.checkBoxClosedPopulation.isChecked():
                qCatchValueTwo = np.random.rand(populationSize)
                fishDeath = np.random.rand(populationSize)
            elif self.checkBoxOpenPopulation.isChecked():
                qCatchValueTwo = np.random.rand(populationSize * 3)
                fishDeath = np.random.rand(populationSize * 3)

            # Declare variables
            secondPassFishes = 0
            recapturedTaggedFish = 0
            pointHolder = []

            # #################################### START SECOND CAPTURE ################################################# #
            for k in range(len(qCatchValueTwo)):
                fishPopulation[k].SetCaptureProbabilityTwo(qCatchValueTwo[k])
                # CLOSED POPULATION:
                if self.checkBoxClosedPopulation.isChecked():
                    # First scenario: no sub reach parameter:
                    if self.checkBoxNoSubreach.isChecked():
                        # Do this first scenario if there is equal probability between the two samples:
                        if self.checkBoxCaptureEqual.isChecked():
                            if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInput.value():
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                        # Do this second scenario if sample two has different capture variability from first capture sample:
                        elif self.checkBoxCaptureVary.isChecked():
                            if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInputVaryTwo.value():
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                        # Do this third scenario if fish has random capture probability as well:
                        elif self.checkBoxCaptureRandomPerFish.isChecked():
                            randomCaptureProbabilityRoll = np.random.rand(1)
                            if fishPopulation[k].captureProbQTwo <= randomCaptureProbabilityRoll[0]:
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                    # Second scenario: varied sub reach parameter:
                    elif self.checkBoxVariedSubreach.isChecked():
                        # Do this first scenario if there is equal probability between the two samples:
                        if self.checkBoxCaptureEqual.isChecked():
                            # Check if it's in the sub reach in the first place, we use initial position as there is no
                            # immigration or emigration
                            if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                                # Can we capture it?
                                if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInput.value():
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                        # Do this second scenario if sample two has different capture variability from first capture sample:
                        elif self.checkBoxCaptureVary.isChecked():
                            # Check if it's in the sub reach in the first place:
                            if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                                # Can we capture it?
                                if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInputVaryTwo.value():
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                        # Do this third scenario if fish has random capture probability as well:
                        elif self.checkBoxCaptureRandomPerFish.isChecked():
                            # Check if it's in the sub reach in the first place:
                            if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                                # Can we capture it?
                                randomCaptureProbabilityRoll = np.random.rand(1)
                                if fishPopulation[k].captureProbQTwo <= randomCaptureProbabilityRoll[0]:
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')

                # OPEN POPULATION SCENARIO
                elif self.checkBoxOpenPopulation.isChecked():
                    # Mortality an option?
                    if fishDeath[k] <= self.openPopulationMoralityInput.value():
                        # Kill the fish:
                        fishPopulation[k].SetMortality(0)

                    # MOVEMENT:
                    migrationDistance = self.migrationDistanceBox.value()
                    highBoundMovementRange = fishPopulation[k].GetSubReachPos() + (REACH_SIZE * migrationDistance)
                    # https://www.geeksforgeeks.org/scipy-stats-beta-python/
                    betaX = np.linspace(0, 1, 100)
                    y1 = beta.pdf(betaX, BETA_DISTRIBUTION, BETA_DISTRIBUTION)
                    # lowBoundMovementRange = fishPopulation[k].GetSubReachPos() - (REACH_SIZE * self.migrationDistanceBox.value())
                    # highBoundMovementRange = fishPopulation[k].GetSubReachPos() + (REACH_SIZE * self.migrationDistanceBox.value())
                    # First 1/3 of area: D (downstream),  Second 1/3 of area: C (central), Third 1/3 of area: U (upstream)
                    correction = self.migrationRateBox.value() - 0.5
                    point = np.random.randint(0, len(betaX))
                    counter = 0
                    while point in pointHolder or counter <= 100:
                        point = np.random.randint(0, len(betaX))
                        counter += 1
                        if counter == 100:
                            pointHolder.clear()

                    if betaX[point] + correction < 0:
                        if (y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)) > highBoundMovementRange:
                            fishMove = highBoundMovementRange
                            fishPopulation[k].SetMigrationDistance(-fishMove)
                            fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() - fishMove)
                        else:
                            fishMove = y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)
                            fishPopulation[k].SetMigrationDistance(-fishMove)
                            fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() - fishMove)
                    elif betaX[point] + correction >= 0:
                        if (y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)) > highBoundMovementRange:
                            fishMove = highBoundMovementRange
                            fishPopulation[k].SetMigrationDistance(fishMove)
                            fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)
                        else:
                            fishMove = y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)
                            fishPopulation[k].SetMigrationDistance(fishMove)
                            fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)

                    # Second scenario: varied sub reach parameter:
                    if self.checkBoxVariedSubreach.isChecked():
                        # Do this first scenario if there is equal probability between the two samples:
                        if self.checkBoxCaptureEqual.isChecked():
                            # Check if it's in the sub reach in the first place:
                            if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                                # Can't capture a dead fish:
                                if fishPopulation[k].GetMortality() == 1:
                                    # Can we capture it?
                                    if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInput.value():
                                        secondPassFishes += 1
                                        fishPopulation[k].SetRecaughtStat('NO TAG')
                                        if fishPopulation[k].tagged == 1:
                                            recapturedTaggedFish += 1
                                            fishPopulation[k].SetRecaughtStat('YES')
                        # Do this second scenario if sample two has different capture variability from first capture sample:
                        elif self.checkBoxCaptureVary.isChecked():
                            # Check if it's in the sub reach in the first place:
                            if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                                # Can't capture a dead fish:
                                if fishPopulation[k].GetMortality() == 1:
                                    # Can we capture it?
                                    if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInputVaryTwo.value():
                                        secondPassFishes += 1
                                        fishPopulation[k].SetRecaughtStat('NO TAG')
                                        if fishPopulation[k].tagged == 1:
                                            recapturedTaggedFish += 1
                                            fishPopulation[k].SetRecaughtStat('YES')
                        # Do this third scenario if fish has random capture probability as well:
                        elif self.checkBoxCaptureRandomPerFish.isChecked():
                            # Check if it's in the sub reach in the first place:
                            if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    # Can we capture it?
                                    randomCaptureProbabilityRoll = np.random.rand(1)
                                    if fishPopulation[k].captureProbQTwo <= randomCaptureProbabilityRoll[0]:
                                        secondPassFishes += 1
                                        fishPopulation[k].SetRecaughtStat('NO TAG')
                                        if fishPopulation[k].tagged == 1:
                                            recapturedTaggedFish += 1
                                            fishPopulation[k].SetRecaughtStat('YES')
            # End Second Capture Pass

            # Estimation formula
            estimatedSampleSizeN = (((firstPassMarkedFishes + 1) * (secondPassFishes + 1)) / (recapturedTaggedFish + 1)) - 1

            simulationResults.append(estimatedSampleSizeN)
            # ######## START RAW DATA SAVING, ALLOWS USER TO VIEW RESULTS OF EACH SIMULATION ######################### #

            # Put this test result in a list for raw  data viewing:
            if i == 0:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes, recapturedTaggedFish, fishPopulation)
                testResultsArray = [testResult]
            else:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes, recapturedTaggedFish, fishPopulation)
                testResultsArray.insert(i, testResult)

        # Create an np array for the results:
        arrayResult = np.array(simulationResults)
        # Add the overall summary for this result to the saved array for all simulations
        thisSimulation = SimulationParameters(numTrials, arrayResult.mean(), populationSize, testResultsArray)
        thisSimulation.SetParameterString(populationType + "\n" + captureProbabilityString + "\n" + captureProbabilityType + "\n" + tagLossType + "\n" \
                                          + subReachType + "\n" + migrationString)
        simulationSaves.append(thisSimulation)

        # Add this to the data log:
        self.loadSimulationNumberInput.addItem(str(len(simulationSaves)))

        self.runSimulationButton.setEnabled(True)

        return arrayResult

    #################################################################################
    # Multi-thread Worker: Progress Update, catches what is emitted
    #################################################################################
    def threadProgress(self, n):
        # emitted goes here...
        # Need to declare globally first, then do
        # global x, then set it:
        # https://www.youtube.com/watch?v=fKl2JW_qrso&t=2078s
        x = "%d%% done" % n
        print(x)

    #################################################################################
    # Multi-thread Worker: Simulation in multiprocess
    #################################################################################
    def simulateMultiProcStyle(self, simulationResult, i):
        # Be able to save data for each simulation:
        # Generate random numbers for capture probability:
        if self.checkBoxClosedPopulation.isChecked():
            qCatchValue = np.random.rand(populationSize)
        elif self.checkBoxOpenPopulation.isChecked():
            qCatchValue = np.random.rand(populationSize * 3)
        tagLossIndex = []
        fishLocation = []

        # For Open Population, do three areas:
        if self.checkBoxOpenPopulation.isChecked():
            # Range size - 100 to 200, [-inf, 0) is out of bounds, [0, 100] is the study reach default, [101, to inf) is out of bounds
            # First 1/3 of area: D (downstream),  Second 1/3 of area: C (central), Third 1/3 of area: U (upstream)
            fishLocation.extend(np.random.randint(-REACH_SIZE, 1, populationSize))
            fishLocation.extend(np.random.randint(1, REACH_SIZE + 1, populationSize))
            fishLocation.extend(np.random.randint(REACH_SIZE + 1, REACH_SIZE * 2, populationSize))
        # Else we do one whole study reach:
        else:
            # Range size: 0 to 100
            fishLocation = [np.random.randint(0, REACH_SIZE + 1) for p in range(0, populationSize)]
            # Set initial location of fish:

        # Get lower and upper bounds
        self.SetSubReachBoundary()

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

            # Set location of the fish:
            fishPopulation[m].SetSubReachPos(fishLocation[m])

        # ################################START THE FIRST PASS ################################################# #
        firstPassMarkedFishes = 0
        # First set of fish population marked.
        for j in range(len(qCatchValue)):
            # ############################# If sub reach is not a factor: ############################# #
            if self.checkBoxNoSubreach.isChecked():
                # Do the first scenario if there is equal or varying probability between samples:
                if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                    if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                        # Tag the fish
                        fishPopulation[j].SetFishTag(1)
                        tagLossIndex.append(j)
                        # Increment Counter:
                        firstPassMarkedFishes += 1
                        fishPopulation[j].SetRecaughtStat('FIRST PASS')
                # Do this scenario if each fish has a random probability of getting captured:
                elif self.checkBoxCaptureRandomPerFish.isChecked():
                    randomCaptureProbabilityRoll = np.random.rand(1)
                    if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                        # Tag the fish
                        fishPopulation[j].SetFishTag(1)
                        tagLossIndex.append(j)
                        # Increment Counter:
                        firstPassMarkedFishes += 1
                        fishPopulation[j].SetRecaughtStat('FIRST PASS')
                # End this scenario
            # ############################# End the no sub reach parameter ############################# #
            # If sub reach is a factor, catch only those in study
            elif self.checkBoxVariedSubreach.isChecked():
                # Do the first scenario if there is equal or varying probability between samples:
                if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                    # Capture only if the fish is in the range:
                    if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                        if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                            # Tag the fish
                            fishPopulation[j].SetFishTag(1)
                            tagLossIndex.append(j)
                            # Increment Counter:
                            firstPassMarkedFishes += 1
                            fishPopulation[j].SetRecaughtStat('FIRST PASS')
                # Do this scenario if each fish has a random probability of getting captured:
                elif self.checkBoxCaptureRandomPerFish.isChecked():
                    randomCaptureProbabilityRoll = np.random.rand(1)
                    if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                        if fishPopulation[j].captureProbQ <= randomCaptureProbabilityRoll[0]:
                            # Tag the fish
                            fishPopulation[j].SetFishTag(1)
                            tagLossIndex.append(j)
                            # Increment Counter:
                            firstPassMarkedFishes += 1
                            fishPopulation[j].SetRecaughtStat('FIRST PASS')
                # End this scenario
            # End the normal sub reach parameter
        # ############################################## BREAK ################################################# #
        # Tag loss scenario:
        tagLossCounter = 0
        # See if the fish loses its tag after being tagged.
        if self.checkBoxTagLoss.isChecked():
            tagLossValue = np.random.rand(len(tagLossIndex))
            for v in range(len(tagLossIndex)):
                fishPopulation[tagLossIndex[v]].SetTagLoss(tagLossValue[v])
                if fishPopulation[tagLossIndex[v]].tagLoss <= tagLossVar:
                    fishPopulation[tagLossIndex[v]].SetFishTag(0)
                    tagLossCounter += 1

        # ########################################### END BREAK ################################################# #
        # self.simulationParameterPrint.append('Fishes caught during first pass: ' + str(firstPassMarkedFishes))
        # ################################ START SECOND PASS ################################################# #
        # Create new catch values
        # Generate random numbers for capture probability:
        if self.checkBoxClosedPopulation.isChecked():
            qCatchValueTwo = np.random.rand(populationSize)
            fishDeath = np.random.rand(populationSize)
        elif self.checkBoxOpenPopulation.isChecked():
            qCatchValueTwo = np.random.rand(populationSize * 3)
            fishDeath = np.random.rand(populationSize * 3)

        # Declare variables
        secondPassFishes = 0
        recapturedTaggedFish = 0
        pointHolder = []

        # #################################### START SECOND CAPTURE ################################################# #
        for k in range(len(qCatchValueTwo)):
            fishPopulation[k].SetCaptureProbabilityTwo(qCatchValueTwo[k])
            # CLOSED POPULATION:
            if self.checkBoxClosedPopulation.isChecked():
                # First scenario: no sub reach parameter:
                if self.checkBoxNoSubreach.isChecked():
                    # Do this first scenario if there is equal probability between the two samples:
                    if self.checkBoxCaptureEqual.isChecked():
                        if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInput.value():
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                secondPassFishes += 1
                                fishPopulation[k].SetRecaughtStat('NO TAG')
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                                    fishPopulation[k].SetRecaughtStat('YES')
                    # Do this second scenario if sample two has different capture variability from first capture sample:
                    elif self.checkBoxCaptureVary.isChecked():
                        if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInputVaryTwo.value():
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                secondPassFishes += 1
                                fishPopulation[k].SetRecaughtStat('NO TAG')
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                                    fishPopulation[k].SetRecaughtStat('YES')
                    # Do this third scenario if fish has random capture probability as well:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        randomCaptureProbabilityRoll = np.random.rand(1)
                        if fishPopulation[k].captureProbQTwo <= randomCaptureProbabilityRoll[0]:
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                secondPassFishes += 1
                                fishPopulation[k].SetRecaughtStat('NO TAG')
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                                    fishPopulation[k].SetRecaughtStat('YES')
                # Second scenario: varied sub reach parameter:
                elif self.checkBoxVariedSubreach.isChecked():
                    # Do this first scenario if there is equal probability between the two samples:
                    if self.checkBoxCaptureEqual.isChecked():
                        # Check if it's in the sub reach in the first place, we use initial position as there is no
                        # immigration or emigration
                        if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                            # Can we capture it?
                            if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInput.value():
                                secondPassFishes += 1
                                fishPopulation[k].SetRecaughtStat('NO TAG')
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                                    fishPopulation[k].SetRecaughtStat('YES')
                    # Do this second scenario if sample two has different capture variability from first capture sample:
                    elif self.checkBoxCaptureVary.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                            # Can we capture it?
                            if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInputVaryTwo.value():
                                secondPassFishes += 1
                                fishPopulation[k].SetRecaughtStat('NO TAG')
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                                    fishPopulation[k].SetRecaughtStat('YES')
                    # Do this third scenario if fish has random capture probability as well:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach:
                            # Can we capture it?
                            randomCaptureProbabilityRoll = np.random.rand(1)
                            if fishPopulation[k].captureProbQTwo <= randomCaptureProbabilityRoll[0]:
                                secondPassFishes += 1
                                fishPopulation[k].SetRecaughtStat('NO TAG')
                                if fishPopulation[k].tagged == 1:
                                    recapturedTaggedFish += 1
                                    fishPopulation[k].SetRecaughtStat('YES')

            # OPEN POPULATION SCENARIO
            elif self.checkBoxOpenPopulation.isChecked():
                # Mortality an option?
                if fishDeath[k] <= self.openPopulationMoralityInput.value():
                    # Kill the fish:
                    fishPopulation[k].SetMortality(0)

                # MOVEMENT:
                migrationDistance = self.migrationDistanceBox.value()
                highBoundMovementRange = fishPopulation[k].GetSubReachPos() + (REACH_SIZE * migrationDistance)
                # https://www.geeksforgeeks.org/scipy-stats-beta-python/
                betaX = np.linspace(0, 1, 100)
                y1 = beta.pdf(betaX, BETA_DISTRIBUTION, BETA_DISTRIBUTION)
                # lowBoundMovementRange = fishPopulation[k].GetSubReachPos() - (REACH_SIZE * self.migrationDistanceBox.value())
                # highBoundMovementRange = fishPopulation[k].GetSubReachPos() + (REACH_SIZE * self.migrationDistanceBox.value())
                # First 1/3 of area: D (downstream),  Second 1/3 of area: C (central), Third 1/3 of area: U (upstream)
                correction = self.migrationRateBox.value() - 0.5
                point = np.random.randint(0, len(betaX))
                counter = 0
                while point in pointHolder or counter <= 100:
                    point = np.random.randint(0, len(betaX))
                    counter += 1
                    if counter == 100:
                        pointHolder.clear()

                if betaX[point] + correction < 0:
                    if (y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)) > highBoundMovementRange:
                        fishMove = highBoundMovementRange
                        fishPopulation[k].SetMigrationDistance(-fishMove)
                        fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() - fishMove)
                    else:
                        fishMove = y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)
                        fishPopulation[k].SetMigrationDistance(-fishMove)
                        fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() - fishMove)
                elif betaX[point] + correction >= 0:
                    if (y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)) > highBoundMovementRange:
                        fishMove = highBoundMovementRange
                        fishPopulation[k].SetMigrationDistance(fishMove)
                        fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)
                    else:
                        fishMove = y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)
                        fishPopulation[k].SetMigrationDistance(fishMove)
                        fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)

                # Second scenario: varied sub reach parameter:
                if self.checkBoxVariedSubreach.isChecked():
                    # Do this first scenario if there is equal probability between the two samples:
                    if self.checkBoxCaptureEqual.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                            # Can't capture a dead fish:
                            if fishPopulation[k].GetMortality() == 1:
                                # Can we capture it?
                                if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInput.value():
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                    # Do this second scenario if sample two has different capture variability from first capture sample:
                    elif self.checkBoxCaptureVary.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                            # Can't capture a dead fish:
                            if fishPopulation[k].GetMortality() == 1:
                                # Can we capture it?
                                if fishPopulation[k].captureProbQTwo <= self.captureProbabilityInputVaryTwo.value():
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                    # Do this third scenario if fish has random capture probability as well:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        # Check if it's in the sub reach in the first place:
                        if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                            # Can't capture a dead fish:
                            if not fishPopulation[k].GetMortality() == 0:
                                # Can we capture it?
                                randomCaptureProbabilityRoll = np.random.rand(1)
                                if fishPopulation[k].captureProbQTwo <= randomCaptureProbabilityRoll[0]:
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
        # End Second Capture Pass

        # Estimation formula
        estimatedSampleSizeN = (((firstPassMarkedFishes + 1) * (secondPassFishes + 1)) / (recapturedTaggedFish + 1)) - 1

        simulationResult.append(estimatedSampleSizeN)
        # ######## START RAW DATA SAVING, ALLOWS USER TO VIEW RESULTS OF EACH SIMULATION ######################### #

    #################################################################################
    # Multi-thread Worker: Function to execute
    #################################################################################
    def threadExecute(self, a, b, progress_callback):

        # https://python-forum.io/Thread-Parsing-infor-from-scraped-files
        # https://docs.python.org/3.3/library/concurrent.futures.html
        # https://christophergs.github.io/python/2018/03/25/python-concurrent-futures/

        # for n in range(0, 5):
        # threadProgress catches what is emitted:
        # print(a)  - prints placeholder argument 1
        # print(b) - prints placeholder argument 2
        # self.whatever()
        # progress_callback.emit(n*100/4)

        # Start multiprocessing:
        global simulationResult
        simulationResult = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(self.simulateMultiProcStyle(simulationResult, i)) for i in range(numTrials)]

            # for f in concurrent.futures.as_completed(results):
            #    try:
            #        print(f.result())
            #    except Exception as exc:
            #        print('%r generated an exception %s' % ('Error Futures', exc))
            #    else:
            #        print('%r' % 'Error Futures')

        # Goes to threadResult function`
        return "Done."

    #################################################################################
    # Multi-thread Worker: Results of thread Execute
    #################################################################################
    def threadResult(self, s):
        print(s)

    #################################################################################
    # Multi-thread Worker: Thread Completed
    #################################################################################
    def threadComplete(self):

        print("Thread Complete.")

        arrayResult = np.array(simulationResult)

        # Print out results
        self.simulationParameterPrint.append('Mean Population estimation: ' + str('{number:.{digits}f}'.format(number=arrayResult.mean(), digits=4)))
        # Print out Parameters
        self.simulationParameterPrint.append("Actual Population Size: " + str(populationSize) + "\tType: " + populationType)
        self.simulationParameterPrint.append(captureProbabilityString + "\tType: "
                                             + captureProbabilityType)
        self.simulationParameterPrint.append(tagLossType + "\t\tSubreach Type: " + subReachType)
        self.simulationParameterPrint.append("Number of Trials: " + str(numTrials))
        self.simulationParameterPrint.append(migrationString)

        # Graph:
        # count number in each bin
        bins = np.linspace(min(simulationResult), max(simulationResult))
        hist, _ = np.histogram(simulationResult, bins)
        plt.figure(figsize=[10, 8])
        # plt.bar(bin_edges[:-1], hist, width=0.5, color='#0504aa', alpha=0.7)
        plt.bar(bins[:-1], hist, label=str(numTrials) + ' trials', width=1)
        # plt.plot(bins[:-1], hist, 'r-', lw=5)
        plt.axvline(populationSize, color='g', linestyle="dashed", lw=2, label=str('True Population Size'))
        plt.axvline(arrayResult.mean(), color='r', lw=2, label=str('Simulation Mean'))
        plt.xlim(min(bins), max(bins))
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Population Estimate\n Mean Population Estimation = ' + str('{number:.{digits}f}'.format(number=arrayResult.mean(), digits=2)), fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.title('Population Estimate Simulation N = ' + str(populationSize), fontsize=15)
        plt.legend(loc='best')
        plt.show()
        # Re-enable simulations
        self.runSimulationButton.setEnabled(True)

    #################################################################################
    # Multi-thread Worker: Set Connections, then run
    #################################################################################
    def threadSetAndExecute(self):
        worker = Worker(self.threadExecute, "placeholderArgument1", "placeholderArgument2")
        worker.signals.result.connect(self.threadResult)
        worker.signals.finished.connect(self.threadComplete)
        worker.signals.progress.connect(self.threadProgress)

        # Execute thread
        self.threadpool.start(worker)

    #################################################################################
    # Simulation MULTIPROCESS / MULTI-THREADING STYLE
    #################################################################################
    def simulateMulti(self):
        self.threadSetAndExecute()

    #################################################################################
    # Simulation and then plot histogram
    #################################################################################
    def simulateAndPlot(self):
        self.runSimulationButton.setEnabled(False)
        self.simulationParameterPrint.clear()
        self.simulateMulti()

        # Declare array for results:
        # simulationResults = []
        # arrayResult = self.simulate(simulationResults)

        # Graph:
        # count number in each bin
        # bins = np.linspace(min(simulationResults), max(simulationResults))
        # hist, _ = np.histogram(simulationResults, bins)
        # plt.figure(figsize=[10, 8])
        # plt.bar(bin_edges[:-1], hist, width=0.5, color='#0504aa', alpha=0.7)
        # plt.bar(bins[:-1], hist, label=str(numTrials) + ' trials', width=1)
        # plt.plot(bins[:-1], hist, 'r-', lw=5)
        # plt.axvline(populationSize, color='g', linestyle="dashed", lw=2, label=str('True Population Size'))
        # plt.axvline(arrayResult.mean(), color='r', lw=2, label=str('Simulation Mean'))
        # plt.xlim(min(bins), max(bins))
        # plt.grid(axis='y', alpha=0.75)
        # plt.xlabel('Population Estimate\n Mean Population Estimation = ' + str('{number:.{digits}f}'.format(number=arrayResult.mean(), digits=2)), fontsize=15)
        # plt.ylabel('Frequency', fontsize=15)
        # plt.xticks(fontsize=15)
        # plt.yticks(fontsize=15)
        # plt.ylabel('Frequency', fontsize=15)
        # plt.title('Population Estimate Simulation N = ' + str(populationSize), fontsize=15)
        # plt.legend(loc='best')
        # plt.show()
        # https://www.datacamp.com/community/tutorials/histograms-matplotlib
        # https://www.youtube.com/watch?time_continue=79&v=Z2zUGmqIDto

        # Update simulation array max input in combobox:

    #################################################################################
    # SIMULATION - TAB TWO
    #################################################################################
    def simulateFishes(self):

        # QMessageBox.information(self, "A Good Msage", "Success. Results shown in the results box.")

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
        # Enable Save Button
        self.saveResultsButton.setEnabled(True)
        self.refreshResultsButton.setEnabled(True)
        self.clearDataButton.setEnabled(True)
        self.viewImageButton.setEnabled(True)
        self.populationGraphCheckBox.setEnabled(True)
        # Simulate and plot
        self.simulateAndPlot()


#################################################################################
# MAIN FUNCTION
#################################################################################
if __name__ == "__main__":
    app = QApplication([])
    ui = MainWindow()
    sys.exit(app.exec_())
