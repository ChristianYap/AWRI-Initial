#################################################################################
# Name: Christian Yap
# Description: Lincoln Peterson with Chapman's Estimator Program:
# Estimates population using the Lincoln Peterson Chapman Estimator, as well as
# allowing users to change assumed assumptions and parameters and get a simulation.
# Version: 1.0, Created August 2019
# References: https://github.com/ColinDuquesnoy/QDarkStyleSheet
#################################################################################
import sys
import qdarkstyle
import os
import csv
import time
import traceback
import concurrent.futures
import multiprocessing
import scipy
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from MainWindow import Ui_MainWindow
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from SimulationParameters import SimulationParameters
from Fish import Fish
from TestResults import TestResults
from scipy.stats import beta, skew

# Global Variables
REACH_SIZE = 100
BETA_DISTRIBUTION = 2.70
simulationSaves = []
global simulationResult
global testResultArray


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
        self.saveTrials = QButtonGroup()

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
        self.pushButtonShowDistribution.setVisible(False)

        self.subReachMovementOption.setEnabled(False)
        self.subReachMovementOption.setVisible(False)
        self.subReachMovementOptionBox.setEnabled(False)
        self.subReachMovementOptionBox.setVisible(False)

        self.mortalityProbabilityTitle.setVisible(False)
        self.saveResultsButton.setEnabled(False)
        self.clearDataButton.setEnabled(False)
        self.loadSimulationNumberInput.setCurrentText('1')

        self.saveSpecificTrialCheckBox.setChecked(True)

        self.progressBar.setVisible(False)
        self.actionSave_Results.setVisible(False)

        # Read only:
        self.simulationReviewer.setReadOnly(True)
        self.simulationParameterPrint.setReadOnly(True)
        self.resultScreenOne.setReadOnly(True)
        # Font Size
        self.simulationParameterPrint.setFontPointSize(10)
        self.simulationReviewer.setFontPointSize(10)

        # Preset variables
        global defaultStyle
        defaultStyle = self.styleSheet()
        global stopSimulation
        stopSimulation = False

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

        # Group Four: Save Option
        self.saveTrials.addButton(self.saveSpecificTrialCheckBox, 1)
        self.saveTrials.addButton(self.saveAllTrialsSeparateCheckBox,2)
        self.saveTrials.addButton(self.saveAllTrialsCheckBox, 3)

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
        self.pushButtonShowDistribution.clicked.connect(self.betaDistribution)
        self.saveResultsButton.clicked.connect(self.SaveResults)

        # Menu
        self.actionExit.triggered.connect(self.ActionExit)
        self.actionUser_Manual.triggered.connect(self.UserManual)
        self.actionNight_Mode.triggered.connect(self.NightMode)

        # Stop Simulation
        self.stopSimulationButton.clicked.connect(self.StopSimulation)

    #################################################################################
    # Stop Simulation
    #################################################################################
    def NightMode(self):

        if self.actionNight_Mode.isChecked():
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        else:
            global defaultStyle
            app.setStyleSheet(defaultStyle)

    #################################################################################
    # Stop Simulation
    #################################################################################
    def StopSimulation(self):
        global stopSimulation
        stopSimulation = True
        print("Stopping simulation...")

    #################################################################################
    # User Manual
    #################################################################################
    def UserManual(self):
        QMessageBox.information(self, "User Manual", "User Manual is available at the following link:\n"
                                               "https://github.com/staddlez/AWRI-Initial\n(Hold Ctrl + C to copy link)")

    #################################################################################
    # Exit
    #################################################################################
    def ActionExit(self):
        self.close()

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

    #################################################################################
    # Beta Distribution Graph
    #################################################################################
    def betaDistribution(self):
        correction = self.migrationRateBox.value() - 0.5
        # https://www.geeksforgeeks.org/scipy-stats-beta-python/
        betaX = np.linspace(0, 1, 100)
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html
        # beta.pdf(x,a,b) x = points; a = variable a and b = variable b
        y1 = beta.pdf(betaX, BETA_DISTRIBUTION, BETA_DISTRIBUTION)
        plt.plot(betaX + correction, y1 + REACH_SIZE * self.migrationDistanceBox.value() - (BETA_DISTRIBUTION / 2), "*")
        plt.ylabel('Movement Distance (% of subreach)', fontsize=15)
        plt.xlabel('x', fontsize=15)
        plt.show()

    #################################################################################
    # Migration Distance (0 - 100 - 200 % ) of subreach slide:
    #################################################################################
    def MigrationDistanceSlider(self):
        global migrationDistVal
        global migrationDistStatus

        self.migrationDistanceBox.setValue(self.migrationDistanceSlider.value() / 100)
        migrationDistVal = self.migrationDistanceSlider.value() / 100
        migrationDistStatus = '\nMigration Distance: ' + str(migrationDistVal)

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
        plt.grid(True)
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
            plt.grid(True)
            plt.show()

    #################################################################################
    # Checks File Path
    #################################################################################
    def CheckFile(self, path, i):
        path = os.path.expanduser(path)
        root, ext = os.path.splitext(os.path.expanduser(path))
        dir = os.path.dirname(root)
        fname = os.path.basename(root)
        candidate = fname + ext
        index = i
        ls = set(os.listdir(dir))
        # while candidate in ls:
        candidate = "{}_{}{}".format(fname, index, ext)
        return os.path.join(dir, candidate).replace("\\", "/")

    #################################################################################
    # Save Results
    #################################################################################
    def SaveResults(self):
        try:
            path = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'), "CSV Files(*.csv)")

            # If for one trial:
            if self.saveSpecificTrialCheckBox.isChecked():
                # QMessageBox.about(self, "Status Message", "You must select a specific trial to export.")
                if path[0] != '':
                    with open(path[0], 'w', newline='') as csv_file:
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
                print('File generated.')

                # Get all test data
                newPath = self.CheckFile(path[0], "master")
                # Now we write the raw data
                if newPath != '':
                    with open(newPath, 'w', newline='') as csv_file:
                        writer = csv.writer(csv_file, dialect='excel', delimiter=',')
                        headers = []
                        for column in range(self.tableRawTestData.columnCount()):
                            header = self.tableRawTestData.horizontalHeaderItem(column)
                            if header is not None:
                                headers.append(header.text())
                            else:
                                headers.append("Column " + str(column))
                        writer.writerow(headers)
                        for row in range(self.tableRawTestData.rowCount()):
                            rowdata = []
                            for column in range(self.tableRawTestData.columnCount()):
                                item = self.tableRawTestData.item(row, column)
                                if item is not None:
                                    rowdata.append(item.text())
                                else:
                                    rowdata.append('')
                            writer.writerow(rowdata)

                        summary = self.simulationReviewer.toPlainText()
                        rowdata.clear()
                        rowdata.append("\n\n")
                        rowdata.append(summary)
                        writer.writerow(rowdata)

                print(str(newPath) + " master file generated.")

            # If for all trials, save in separate files:
            elif self.saveAllTrialsSeparateCheckBox.isChecked():
                # View Trial Results:
                testResults = simulationSaves[int(self.loadSimulationNumberInput.currentText()) - 1].GetTestData()
                newPath = os.path.splitext(path[0])[0]
                for i in range(0, self.tableRawTestData.rowCount()):
                    # Get fish data for that specific test:
                    fishData = testResults[i].GetFishData()
                    # increment filename as needed
                    newPath = self.CheckFile(path[0], i)
                    # Show fish data:
                    self.tableRawFishData.setRowCount(0)
                    for itr in range(0, len(fishData)):
                        numRows = self.tableRawFishData.rowCount()
                        self.tableRawFishData.insertRow(numRows)
                        self.tableRawFishData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbability(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 1, QTableWidgetItem(str(fishData[itr].GetSubReachPos())))
                        self.tableRawFishData.setItem(numRows, 2, QTableWidgetItem(str(fishData[itr].GetFishTag())))
                        self.tableRawFishData.setItem(numRows, 3, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetTagLoss(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 4, QTableWidgetItem(str(fishData[itr].GetMortality())))
                        self.tableRawFishData.setItem(numRows, 5, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetMigrationDistance(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 6, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbabilityTwo(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 7, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetSubReachPosTwo(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 8, QTableWidgetItem(str(fishData[itr].GetRecaughtStat())))

                    # Now we write the raw data
                    if newPath != '':
                        with open(newPath, 'w', newline='') as csv_file:
                            print('By default: Existing files will not overwritten! Saving file...')
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

                    print(str(newPath) + " generated.")

                    # Get all test data
                    newPath = self.CheckFile(path[0], "master")
                    # Now we write the raw data
                    if newPath != '':
                        with open(newPath, 'w', newline='') as csv_file:
                            writer = csv.writer(csv_file, dialect='excel', delimiter=',')
                            headers = []
                            for column in range(self.tableRawTestData.columnCount()):
                                header = self.tableRawTestData.horizontalHeaderItem(column)
                                if header is not None:
                                    headers.append(header.text())
                                else:
                                    headers.append("Column " + str(column))
                            writer.writerow(headers)
                            for row in range(self.tableRawTestData.rowCount()):
                                rowdata = []
                                for column in range(self.tableRawTestData.columnCount()):
                                    item = self.tableRawTestData.item(row, column)
                                    if item is not None:
                                        rowdata.append(item.text())
                                    else:
                                        rowdata.append('')
                                writer.writerow(rowdata)

                            summary = self.simulationReviewer.toPlainText()
                            rowdata.clear()
                            rowdata.append("\n\n")
                            rowdata.append(summary)
                            writer.writerow(rowdata)

                    print(str(newPath) + " master file generated.")
            else:
                # Save in one file, View Trial Results:
                self.tableRawFishData.setRowCount(0)
                testResults = simulationSaves[int(self.loadSimulationNumberInput.currentText()) - 1].GetTestData()
                newPath = path[0]
                for i in range(0, self.tableRawTestData.rowCount()):
                    # Get fish data for that specific test:
                    fishData = testResults[i].GetFishData()
                    # increment filename as needed
                    # Show fish data:
                    for itr in range(0, len(fishData)):
                        numRows = self.tableRawFishData.rowCount()
                        self.tableRawFishData.insertRow(numRows)
                        self.tableRawFishData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbability(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 1, QTableWidgetItem(str(fishData[itr].GetSubReachPos())))
                        self.tableRawFishData.setItem(numRows, 2, QTableWidgetItem(str(fishData[itr].GetFishTag())))
                        self.tableRawFishData.setItem(numRows, 3, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetTagLoss(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 4, QTableWidgetItem(str(fishData[itr].GetMortality())))
                        self.tableRawFishData.setItem(numRows, 5, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetMigrationDistance(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 6, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbabilityTwo(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 7, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetSubReachPosTwo(), digits=2))))
                        self.tableRawFishData.setItem(numRows, 8, QTableWidgetItem(str(fishData[itr].GetRecaughtStat())))

                # Now we write the raw data
                if newPath != '':
                    with open(newPath, 'w', newline='') as csv_file:
                        print('By default: Existing files will not overwritten! Saving file...')
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

                print(str(newPath) + " generated.")

                # Get all test data for MASTER
                newPath = self.CheckFile(path[0], "master")
                # Now we write the raw data
                if newPath != '':
                    with open(newPath, 'w', newline='') as csv_file:
                        writer = csv.writer(csv_file, dialect='excel', delimiter=',')
                        headers = []
                        for column in range(self.tableRawTestData.columnCount()):
                            header = self.tableRawTestData.horizontalHeaderItem(column)
                            if header is not None:
                                headers.append(header.text())
                            else:
                                headers.append("Column " + str(column))
                        writer.writerow(headers)
                        for row in range(self.tableRawTestData.rowCount()):
                            rowdata = []
                            for column in range(self.tableRawTestData.columnCount()):
                                item = self.tableRawTestData.item(row, column)
                                if item is not None:
                                    rowdata.append(item.text())
                                else:
                                    rowdata.append('')
                            writer.writerow(rowdata)

                        summary = self.simulationReviewer.toPlainText()
                        rowdata.clear()
                        rowdata.append("\n\n")
                        rowdata.append(summary)
                        writer.writerow(rowdata)

                print(str(newPath) + " master file generated.")
        except Exception as e:
            print('User cancelled.' + str(e))

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
            self.pushButtonShowDistribution.setVisible(False)

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
            self.pushButtonShowDistribution.setVisible(True)
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
        self.simulationReviewer.append('Mean Population Estimated: ' + str('{number:.{digits}f}'.format(number=template.GetOverallEstimatedPopulation(), digits=0)))
        self.simulationReviewer.append('Actual Population size: ' + str(template.GetActualPopulation()))
        self.simulationReviewer.append('Number of Trials: ' + str(template.GetNumTrials()))
        self.simulationReviewer.append(template.GetParameters())

        # View Trial Results:
        testResults = simulationSaves[inputNumber].GetTestData()

        # Create a empty row at bottom of table
        for trials in range(0, len(testResults)):
            numRows = self.tableRawTestData.rowCount()
            self.tableRawTestData.insertRow(numRows)
            self.tableRawTestData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=testResults[trials].GetEstimatedPopulation(), digits=0))))
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

            self.tableRawTestData.rowCount()

        # Get fish data for that specific test:
        fishData = testResults[rowNum].GetFishData()

        # Show fish data in debug mode:
        if self.actionDebug_Mode.isChecked():
            for itr in range(0, len(fishData)):
                numRows = self.tableRawFishData.rowCount()
                self.tableRawFishData.insertRow(numRows)

                # Capture Parameters:
                fishDataCapOne = fishData[itr].GetCaptureProbability()
                fishDataCapTwo = fishData[itr].GetCaptureProbabilityTwo()
                self.tableRawFishData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishDataCapOne, digits=2))))
                self.tableRawFishData.setItem(numRows, 6, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishDataCapTwo, digits=2))))
                if simulationSaves[inputNumber].GetParamCaptureCategory() == 1:
                    if fishDataCapOne <= simulationSaves[inputNumber].GetParamCaptureOne():
                        self.tableRawFishData.item(numRows, 0).setBackground(QColor(55, 174, 114))
                    if fishDataCapTwo <= simulationSaves[inputNumber].GetParamCaptureTwo():
                        self.tableRawFishData.item(numRows, 6).setBackground(QColor(55, 174, 114))
                elif simulationSaves[inputNumber].GetParamCaptureCategory() == 2:
                    if fishDataCapOne <= fishData[itr].GetParameterCaptureOne()[0]:
                        self.tableRawFishData.item(numRows, 0).setBackground(QColor(55, 174, 114))
                    if fishDataCapTwo <= fishData[itr].GetParameterCaptureTwo()[0]:
                        self.tableRawFishData.item(numRows, 6).setBackground(QColor(55, 174, 114))

                # Subreach One:
                subReachPosOne = fishData[itr].GetSubReachPos()
                self.tableRawFishData.setItem(numRows, 1, QTableWidgetItem(str(subReachPosOne)))
                if simulationSaves[inputNumber].GetBoundApplicable() == 1:
                    if simulationSaves[inputNumber].GetParamLowBound() <= subReachPosOne <= simulationSaves[inputNumber].GetParamHighBound():
                        self.tableRawFishData.item(numRows, 1).setBackground(QColor(55, 174, 114))

                # Tag loss:
                tagStatus = fishData[itr].GetFishTag()
                self.tableRawFishData.setItem(numRows, 2, QTableWidgetItem(str(tagStatus)))
                self.tableRawFishData.setItem(numRows, 3, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetTagLoss(), digits=2))))
                if tagStatus == 0:
                    self.tableRawFishData.item(numRows, 2).setBackground(QColor(223, 36, 36))
                elif tagStatus == 1:
                    self.tableRawFishData.item(numRows, 2).setBackground(QColor(55, 174, 114))

                # Mortality:
                mortalityStatus = fishData[itr].GetMortality()
                self.tableRawFishData.setItem(numRows, 4, QTableWidgetItem(str(mortalityStatus)))
                if mortalityStatus == 0:
                    self.tableRawFishData.item(numRows, 4).setBackground(QColor(223, 36, 36))
                elif mortalityStatus == 1:
                    self.tableRawFishData.item(numRows, 4).setBackground(QColor(55, 174, 114))

                # Migration distance:
                self.tableRawFishData.setItem(numRows, 5, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetMigrationDistance(), digits=2))))

                # Subreach two:
                subReachPosTwo = fishData[itr].GetSubReachPosTwo()
                self.tableRawFishData.setItem(numRows, 7, QTableWidgetItem(str('{number:.{digits}f}'.format(number=subReachPosTwo, digits=2))))
                if simulationSaves[inputNumber].GetBoundApplicable() == 1:
                    if simulationSaves[inputNumber].GetParamLowBound() <= subReachPosTwo <= simulationSaves[inputNumber].GetParamHighBound():
                        self.tableRawFishData.item(numRows, 7).setBackground(QColor(55, 174, 114))

                # Status:
                self.tableRawFishData.setItem(numRows, 8, QTableWidgetItem(str(fishData[itr].GetRecaughtStat())))
        else:
            # Show fish data:
            for itr in range(0, len(fishData)):
                numRows = self.tableRawFishData.rowCount()

                self.tableRawFishData.insertRow(numRows)
                self.tableRawFishData.setItem(numRows, 0, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbability(), digits=2))))
                self.tableRawFishData.setItem(numRows, 1, QTableWidgetItem(str(fishData[itr].GetSubReachPos())))
                self.tableRawFishData.setItem(numRows, 2, QTableWidgetItem(str(fishData[itr].GetFishTag())))
                self.tableRawFishData.setItem(numRows, 3, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetTagLoss(), digits=2))))
                self.tableRawFishData.setItem(numRows, 4, QTableWidgetItem(str(fishData[itr].GetMortality())))
                self.tableRawFishData.setItem(numRows, 5, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetMigrationDistance(), digits=2))))
                self.tableRawFishData.setItem(numRows, 6, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetCaptureProbabilityTwo(), digits=2))))
                self.tableRawFishData.setItem(numRows, 7, QTableWidgetItem(str('{number:.{digits}f}'.format(number=fishData[itr].GetSubReachPosTwo(), digits=2))))
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
            self.resultScreenOne.append(dateNow + " - Estimated Fish Population: " + str('{number:.{digits}f}'.format(number=estimatedSampleSizeN, digits=0)))
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
            captureProbabilityType = "Equal capture probability for all samples"
        if self.checkBoxCaptureVary.isChecked():
            captureProbabilityFish = self.captureProbabilityInput.value()
            captureProbabilityFishTwo = self.captureProbabilityInputVaryTwo.value()
            captureProbabilityString = 'Capture probability for first pass: q = ' + str(captureProbabilityFish) \
                                       + 'Capture probability for second pass: q = ' + str(captureProbabilityFishTwo)
            captureProbabilityType = "Capture probability varying per sample."
        if self.checkBoxCaptureRandomPerFish.isChecked():
            captureProbabilityString = 'Capture Probability: Completely random'
            captureProbabilityType = "Capture Probability: Completely random per fish"

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
            # Need to set boundaries so it doesn't crash for the print out below:
            self.SetSubReachBoundary()
            subReachType = "Varied Subreach Size: " + str(self.subReachMovementOption.value()) + "% of subreach. " + " L-bound:" + str(lowerBoundStudyReach) + ". H-bound: " + str(upperBoundStudyReach)

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

    #################################################################################
    # Subreach Boundaries
    #################################################################################
    def SetSubReachBoundary(self):
        global lowerBoundStudyReach
        global upperBoundStudyReach

        size = (REACH_SIZE * self.subReachMovementOptionBox.value())
        lowerBoundStudyReach = (REACH_SIZE / 2) - (size / 2)
        upperBoundStudyReach = (REACH_SIZE / 2) + (size / 2)

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
    # Multi-processing .....
    #################################################################################
    def threadExecuteTwo(self, a, b, progress_callback):
        global simulationResult
        simulationResult = []
        lock1 = multiprocessing.Lock()
        lock2 = multiprocessing.Lock()
        i = 0
        numberProcess = multiprocessing.cpu_count()
        start_time = time.time()
        while i < numTrials:
            processes = []
            m = 0
            for k in range(0, 10):
                if i < numTrials:
                    process = multiprocessing.Process(target=self.simulateMultiProcStyle(simulationResult, i, lock1, lock2))
                    processes.append(process)
                    process.start()
                    i +=1
                    m +=1
            for k in range(0, m):
                processes[k].join()
        print("--- %s seconds ---" % (time.time() - start_time))
        return "Done"

    #################################################################################
    # Multi-thread Worker: Function to execute
    #################################################################################
    def threadExecute(self, a, b, progress_callback):

        # progress_callback.emit(n*100/4)
        # Start multiprocessing:
        global simulationResult
        simulationResult = []
        start_time = time.time()
        counter = 0
        try:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = [executor.submit(self.simulateMultiProcStyleNoLock(simulationResult, i), i) for i in range(numTrials)]
        except Exception as e:
            print("Encountered an error, try running again:" + str(e))

        print("--- %s seconds ---" % (time.time() - start_time))

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
        # Create an np array for the results:
        arrayResult = np.array(simulationResult)

        # Get Quartiles:
        firstQuart = np.quantile(arrayResult, .25)
        secondQuart = np.quantile(arrayResult, .50)
        thirdQuart = np.quantile(arrayResult, 0.75)
        fourthQuart = np.quantile(arrayResult, 1)

        # Get median:
        median = np.median(arrayResult)

        skewNess = scipy.stats.skew(simulationResult)

        additionalStats = "\nMedian: " + str('{number:.{digits}f}'.format(number=median, digits=2)) + "\nQuartiles [Q1, Q2, Q3, Q4]: " \
                          + str('{number:.{digits}f}'.format(number= firstQuart, digits=2)) + " , " \
                          + str('{number:.{digits}f}'.format(number= secondQuart, digits=2)) + " , " \
                          + str('{number:.{digits}f}'.format(number= thirdQuart, digits=2)) + " , " \
                          + str('{number:.{digits}f}'.format(number= fourthQuart, digits=2)) + "\nCoefficient of Skewness: " \
                          + str('{number:.{digits}f}'.format(number= skewNess, digits=2))

        # Print out results
        self.simulationParameterPrint.append('Mean Population estimation: ' + str('{number:.{digits}f}'.format(number=arrayResult.mean(), digits=2)))
        # Print out Parameters
        self.simulationParameterPrint.append("Actual Population Size: " + str(populationSize) + "\nType: " + populationType)
        self.simulationParameterPrint.append(captureProbabilityString + "\nType: " + captureProbabilityType)
        self.simulationParameterPrint.append(tagLossType + "\nSubreach Type: " + subReachType)
        self.simulationParameterPrint.append("Number of Trials: " + str(numTrials))
        self.simulationParameterPrint.append(migrationString)
        self.simulationParameterPrint.append(additionalStats)

        # Add the overall summary for this result to the saved array for all simulations
        thisSimulation = SimulationParameters(numTrials, arrayResult.mean(), populationSize, testResultsArray)
        thisSimulation.SetParameterString(populationType + "\n" + captureProbabilityString + "\n" + captureProbabilityType + "\n" + tagLossType + "\n" \
                                          + subReachType + "\n" + migrationString + "\n" + additionalStats)
        thisSimulation.SetMedian(median)
        thisSimulation.SetFirstQuart(firstQuart)
        thisSimulation.SetSecondQuart(secondQuart)
        thisSimulation.SetThirdQuart(thirdQuart)
        thisSimulation.SetFirstQuart(fourthQuart)
        thisSimulation.SetSkew(skewNess)
        simulationSaves.append(thisSimulation)

        # Add this to the data log:
        self.loadSimulationNumberInput.addItem(str(len(simulationSaves)))
        # Re-enable simulations
        self.runSimulationButton.setEnabled(True)
        self.progressBar.setVisible(False)

        # For testing - capture probability
        if self.checkBoxCaptureEqual.isChecked():
            thisSimulation.SetParamCaptureCategory(1)
            thisSimulation.SetParamCaptureOne(self.captureProbabilityInput.value())
            thisSimulation.SetParamCaptureTwo(self.captureProbabilityInput.value())
        elif self.checkBoxCaptureVary.isChecked():
            thisSimulation.SetParamCaptureCategory(1)
            thisSimulation.SetParamCaptureOne(self.captureProbabilityInput.value())
            thisSimulation.SetParamCaptureTwo(self.captureProbabilityInputVaryTwo.value())
        elif self.checkBoxCaptureRandomPerFish.isChecked():
            thisSimulation.SetParamCaptureCategory(2)

        if self.checkBoxVariedSubreach.isChecked():
            thisSimulation.SetBoundApplicable(1)
            thisSimulation.SetParamLowBound(lowerBoundStudyReach)
            thisSimulation.SetParamHighBound(upperBoundStudyReach)

        # Thread Complete:
        QMessageBox.about(self, "Status Message", "Simulation Complete. Press OK to display results.")
        # Load the data
        self.loadSimulationNumberInput.setCurrentText(str(self.loadSimulationNumberInput.count()))
        self.tabBox.setCurrentIndex(2)
        self.RefreshResults()
        # Allow user to save data
        self.saveAllTrialsCheckBox.setEnabled(True)
        self.saveSpecificTrialCheckBox.setEnabled(True)
        self.saveAllTrialsSeparateCheckBox.setEnabled(True)
        self.stopSimulationButton.setEnabled(False)

    #################################################################################
    # Multi-thread Worker: Set Connections, then run
    #################################################################################
    def threadSetAndExecute(self, a):
        worker = Worker(self.threadExecute, a, "placeholderArgument2")
        worker.signals.result.connect(self.threadResult)
        worker.signals.finished.connect(self.threadComplete)
        worker.signals.progress.connect(self.threadProgress)

        # Execute thread
        self.threadpool.start(worker)

    #################################################################################
    # Simulation MULTIPROCESS / MULTI-THREADING STYLE
    #################################################################################
    def simulateMulti(self, a):
        self.threadSetAndExecute(a)

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
        self.progressBar.setVisible(True)
        self.progressBar.setEnabled(True)
        self.simulateAndPlot()

    #################################################################################
    # Simulation and then plot histogram
    #################################################################################
    def simulateAndPlot(self):
        global stopSimulation
        stopSimulation = False
        self.runSimulationButton.setEnabled(False)
        self.stopSimulationButton.setEnabled(True)
        self.simulationParameterPrint.clear()
        plt.close()

        if self.checkBoxOpenPopulation.isChecked() and not self.checkBoxClosedPopulation.isChecked():
            plt.close()
            self.simulateMulti(1)
        else:
            # Declare array for results:
            simulationResults = []
            start_time = time.time()
            arrayResult, additionalResults = self.simulate(simulationResults)
            print("--- %s seconds ---" % (time.time() - start_time))

            # Print out results
            meanResult = arrayResult.mean()
            self.simulationParameterPrint.append('Mean Population Estimation: ' + str('{number:.{digits}f}'.format(number= meanResult, digits=0)))
            # Print out Parameters
            self.simulationParameterPrint.append("Actual Population Size: " + str(populationSize) + "\nType: " + populationType)
            self.simulationParameterPrint.append(captureProbabilityString + "\nType: "
                                                 + captureProbabilityType)
            self.simulationParameterPrint.append(tagLossType + "\nSubreach Type: " + subReachType)
            self.simulationParameterPrint.append("Number of Trials: " + str(numTrials))
            self.simulationParameterPrint.append(migrationString)
            self.simulationParameterPrint.append(additionalResults)
            QMessageBox.about(self, "Status Message", "Simulation Complete. Press OK to display results.")
            # Load the data
            self.loadSimulationNumberInput.setCurrentText(str(self.loadSimulationNumberInput.count()))
            self.tabBox.setCurrentIndex(2)
            self.RefreshResults()
            # Save data
            self.saveAllTrialsCheckBox.setEnabled(True)
            self.saveSpecificTrialCheckBox.setEnabled(True)
            self.saveAllTrialsSeparateCheckBox.setEnabled(True)
            self.stopSimulationButton.setEnabled(False)

    #################################################################################
    # Simulate Fishes - CLOSED POPULATION
    #################################################################################
    def simulate(self, simulationResults):
        global stopSimulation
        # Be able to save data for each simulation:
        for i in range(0, numTrials):

            # Need to stop simulation?
            app.processEvents()
            if stopSimulation is True:
                break

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
                        fishPopulation[j].SetParameterCaptureOne(np.random.rand(1))
                        if fishPopulation[j].captureProbQ <= fishPopulation[j].GetParameterCaptureOne():
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
                        if (lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
                            if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                                fishPopulation[j].SetRecaughtStat('FIRST PASS')
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        fishPopulation[j].SetParameterCaptureOne(np.random.rand(1))
                        if (lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
                            if fishPopulation[j].captureProbQ <= fishPopulation[j].GetParameterCaptureOne():
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
                fishPopulation[k].SetSubReachPosTwo(fishLocation[k])
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
                            fishPopulation[k].SetParameterCaptureTwo(np.random.rand(1))
                            if fishPopulation[k].captureProbQTwo <= fishPopulation[k].GetParameterCaptureTwo():
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
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach)  and self.subReachMovementOptionBox.value() > 0:
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
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach)  and self.subReachMovementOptionBox.value() > 0:
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
                            fishPopulation[k].SetParameterCaptureTwo(np.random.rand(1))
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach)  and self.subReachMovementOptionBox.value() > 0:
                                # Can we capture it?
                                if fishPopulation[k].captureProbQTwo <= fishPopulation[k].GetParameterCaptureTwo():
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
                            fishPopulation[k].SetParameterCaptureTwo(np.random.rand(1))
                            if lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach:
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    # Can we capture it?
                                    if fishPopulation[k].captureProbQTwo <= fishPopulation[k].GetParameterCaptureTwo():
                                        secondPassFishes += 1
                                        fishPopulation[k].SetRecaughtStat('NO TAG')
                                        if fishPopulation[k].tagged == 1:
                                            recapturedTaggedFish += 1
                                            fishPopulation[k].SetRecaughtStat('YES')
            # End Second Capture Pass

            # Estimation formula
            estimatedSampleSizeN = (((firstPassMarkedFishes + 1) * (secondPassFishes + 1)) / (recapturedTaggedFish + 1)) - 1
            simulationResults.append(estimatedSampleSizeN)
            self.progressBar.setValue(i*100/numTrials)
            # ######## START RAW DATA SAVING, ALLOWS USER TO VIEW RESULTS OF EACH SIMULATION ######################### #

            # Put this test result in a list for raw  data viewing:
            if i == 0:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes, recapturedTaggedFish, fishPopulation)
                testResultsArray = [testResult]
            else:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes, recapturedTaggedFish, fishPopulation)
                testResultsArray.append(testResult)

        # Create an np array for the results:
        arrayResult = np.array(simulationResults)

        # Get Quartiles:
        firstQuart = np.quantile(arrayResult, .25)
        secondQuart = np.quantile(arrayResult, .50)
        thirdQuart = np.quantile(arrayResult, 0.75)
        fourthQuart = np.quantile(arrayResult, 1)

        # Get median:
        median = np.median(arrayResult)

        # Co-efficient of skewness:
        # https://www.geeksforgeeks.org/scipy-stats-skew-python/
        skewNess = scipy.stats.skew(simulationResults)

        additionalStats = "\nMedian: " + str('{number:.{digits}f}'.format(number=median, digits=2)) + "\nQuartiles [Q1, Q2, Q3, Q4]: " \
                          + str('{number:.{digits}f}'.format(number= firstQuart, digits=2)) + " , " \
                          + str('{number:.{digits}f}'.format(number= secondQuart, digits=2)) + " , " \
                          + str('{number:.{digits}f}'.format(number= thirdQuart, digits=2)) + " , " \
                          + str('{number:.{digits}f}'.format(number= fourthQuart, digits=2)) + "\nCoefficient of Skewness: " \
                          + str('{number:.{digits}f}'.format(number= skewNess, digits=2))

        # Add the overall summary for this result to the saved array for all simulations
        thisSimulation = SimulationParameters(numTrials, arrayResult.mean(), populationSize, testResultsArray)
        thisSimulation.SetParameterString(populationType + "\n" + captureProbabilityString + "\n" + captureProbabilityType + "\n" + tagLossType + "\n" \
                                          + subReachType + "\n" + migrationString + "\n" + additionalStats)
        simulationSaves.append(thisSimulation)

        thisSimulation.SetMedian(median)
        thisSimulation.SetFirstQuart(firstQuart)
        thisSimulation.SetSecondQuart(secondQuart)
        thisSimulation.SetThirdQuart(thirdQuart)
        thisSimulation.SetFirstQuart(fourthQuart)
        thisSimulation.SetSkew(skewNess)

        # For testing - capture probability
        if self.checkBoxCaptureEqual.isChecked():
            thisSimulation.SetParamCaptureCategory(1)
            thisSimulation.SetParamCaptureOne(self.captureProbabilityInput.value())
            thisSimulation.SetParamCaptureTwo(self.captureProbabilityInput.value())
        elif self.checkBoxCaptureVary.isChecked():
            thisSimulation.SetParamCaptureCategory(1)
            thisSimulation.SetParamCaptureOne(self.captureProbabilityInput.value())
            thisSimulation.SetParamCaptureTwo(self.captureProbabilityInputVaryTwo.value())
        elif self.checkBoxCaptureRandomPerFish.isChecked():
            thisSimulation.SetParamCaptureCategory(2)

        if self.checkBoxVariedSubreach.isChecked():
            thisSimulation.SetBoundApplicable(1)
            thisSimulation.SetParamLowBound(lowerBoundStudyReach)
            thisSimulation.SetParamHighBound(upperBoundStudyReach)

        # Add this to the data log:
        self.loadSimulationNumberInput.addItem(str(len(simulationSaves)))
        self.runSimulationButton.setEnabled(True)
        self.progressBar.setVisible(False)

        return arrayResult, additionalStats

    #################################################################################
    # Multi-thread Worker: Simulation in multiprocess
    #################################################################################
    def simulateMultiProcStyleNoLock(self, simulationResult, i):

        global stopSimulation

        if not stopSimulation:
            # Be able to save data for each simulation:
            # Generate random numbers for capture probability for first and second catch:
            if self.checkBoxClosedPopulation.isChecked():
                closedPopulation = True
                openPopulation = False
                qCatchValue = np.random.rand(populationSize)
                qCatchValueTwo = np.random.rand(populationSize)
                fishDeath = np.random.rand(populationSize)
            elif self.checkBoxOpenPopulation.isChecked():
                openPopulation = True
                closedPopulation = False
                qCatchValue = np.random.rand(populationSize * 3)
                qCatchValueTwo = np.random.rand(populationSize * 3)
                fishDeath = np.random.rand(populationSize * 3)

            tagLossIndex = []
            fishLocation = []

            # For Open Population, do three areas:
            if openPopulation and not closedPopulation:
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
                    checkBoxNoSubReach = True
                    checkBoxVariedSubReach = False
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
                        fishPopulation[j].SetParameterCaptureOne(np.random.rand(1))
                        if fishPopulation[j].captureProbQ <= fishPopulation[j].GetParameterCaptureOne():
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
                    checkBoxNoSubReach = False
                    checkBoxVariedSubReach = True
                    # Do the first scenario if there is equal or varying probability between samples:
                    if self.checkBoxCaptureVary.isChecked() or self.checkBoxCaptureEqual.isChecked():
                        # Capture only if the fish is in the range:
                        if (lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
                            if fishPopulation[j].captureProbQ <= self.captureProbabilityInput.value():
                                # Tag the fish
                                fishPopulation[j].SetFishTag(1)
                                tagLossIndex.append(j)
                                # Increment Counter:
                                firstPassMarkedFishes += 1
                                fishPopulation[j].SetRecaughtStat('FIRST PASS')
                    # Do this scenario if each fish has a random probability of getting captured:
                    elif self.checkBoxCaptureRandomPerFish.isChecked():
                        fishPopulation[j].SetParameterCaptureOne(np.random.rand(1))
                        if (lowerBoundStudyReach <= fishPopulation[j].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
                            if fishPopulation[j].captureProbQ <= fishPopulation[j].GetParameterCaptureOne():
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

            # Declare variables
            secondPassFishes = 0
            recapturedTaggedFish = 0
            pointHolder = []

            # #################################### START SECOND CAPTURE ################################################# #
            for k in range(len(qCatchValueTwo)):
                fishPopulation[k].SetCaptureProbabilityTwo(qCatchValueTwo[k])
                # CLOSED POPULATION:
                if closedPopulation and not openPopulation:
                    # First scenario: no sub reach parameter:
                    if checkBoxNoSubReach and not checkBoxVariedSubReach:
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
                            fishPopulation[k].SetParameterCaptureTwo(np.random.rand(1))
                            if fishPopulation[k].captureProbQTwo <= fishPopulation[k].GetParameterCaptureTwo():
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')
                    # Second scenario: varied sub reach parameter:
                    elif checkBoxVariedSubReach and not checkBoxNoSubReach:
                        # Do this first scenario if there is equal probability between the two samples:
                        if self.checkBoxCaptureEqual.isChecked():
                            # Check if it's in the sub reach in the first place, we use initial position as there is no
                            # immigration or emigration
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
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
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
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
                            fishPopulation[k].SetParameterCaptureTwo(np.random.rand(1))
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPos() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
                                # Can we capture it?
                                if fishPopulation[k].captureProbQTwo <= fishPopulation[k].GetParameterCaptureTwo():
                                    secondPassFishes += 1
                                    fishPopulation[k].SetRecaughtStat('NO TAG')
                                    if fishPopulation[k].tagged == 1:
                                        recapturedTaggedFish += 1
                                        fishPopulation[k].SetRecaughtStat('YES')

                # OPEN POPULATION SCENARIO
                elif openPopulation and not closedPopulation:
                    # Mortality an option?
                    if fishDeath[k] <= self.openPopulationMoralityInput.value():
                        # Kill the fish:
                        fishPopulation[k].SetMortality(0)

                    migrationDistance = self.migrationDistanceBox.value()
                    highBoundMovementRange = (REACH_SIZE * migrationDistance)
                    # https://www.geeksforgeeks.org/scipy-stats-beta-python/
                    betaX = np.linspace(0, 1, populationSize)
                    y1 = beta.pdf(betaX, BETA_DISTRIBUTION, BETA_DISTRIBUTION)
                    # lowBoundMovementRange = fishPopulation[k].GetSubReachPos() - (REACH_SIZE * self.migrationDistanceBox.value())
                    # highBoundMovementRange = fishPopulation[k].GetSubReachPos() + (REACH_SIZE * self.migrationDistanceBox.value())
                    # First 1/3 of area: D (downstream),  Second 1/3 of area: C (central), Third 1/3 of area: U (upstream)
                    correction = self.migrationRateBox.value() - 0.5
                    point = np.random.randint(0, len(betaX))
                    counter = 0

                    # find a point that has not been used if that point has been used:
                    while point in pointHolder or counter <= populationSize:
                        point = np.random.randint(0, len(betaX))
                        counter += 1
                        if counter == populationSize:
                            pointHolder.clear()
                        # print(counter)
                    # print("REACH_SIZE:" + str(REACH_SIZE) + " point:" + str(y1[point]) + " migration Distance: " + str(migrationDistance) + " beta:" + str(BETA_DISTRIBUTION))
                    newLocation = y1[point] + REACH_SIZE * migrationDistance - (BETA_DISTRIBUTION / 2)
                    if betaX[point] + correction < 0:
                        if self.migrationDistanceBox.value() > 0:
                            if newLocation > highBoundMovementRange:
                                fishMove = highBoundMovementRange
                                fishPopulation[k].SetMigrationDistance(-fishMove)
                                fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() - fishMove)
                            else:
                                fishMove = newLocation
                                fishPopulation[k].SetMigrationDistance(-fishMove)
                                fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() - fishMove)
                        elif betaX[point] + correction >= 0:
                            if newLocation > highBoundMovementRange:
                                fishMove = highBoundMovementRange
                                fishPopulation[k].SetMigrationDistance(fishMove)
                                fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)
                            else:
                                fishMove = newLocation
                                fishPopulation[k].SetMigrationDistance(fishMove)
                                fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)
                        else:
                            fishMove = 0
                            fishPopulation[k].SetMigrationDistance(fishMove)
                            fishPopulation[k].SetSubReachPosTwo(fishPopulation[k].GetSubReachPos() + fishMove)

                    # Second scenario: varied sub reach parameter:
                    if self.checkBoxVariedSubreach.isChecked():
                        # Do this first scenario if there is equal probability between the two samples:
                        if self.checkBoxCaptureEqual.isChecked():
                            # Check if it's in the sub reach in the first place:
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
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
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
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
                            fishPopulation[k].SetParameterCaptureTwo(np.random.rand(1))
                            if (lowerBoundStudyReach <= fishPopulation[k].GetSubReachPosTwo() <= upperBoundStudyReach) and self.subReachMovementOptionBox.value() > 0:
                                # Can't capture a dead fish:
                                if not fishPopulation[k].GetMortality() == 0:
                                    # Can we capture it?
                                    if fishPopulation[k].captureProbQTwo <= fishPopulation[k].GetParameterCaptureTwo():
                                        secondPassFishes += 1
                                        fishPopulation[k].SetRecaughtStat('NO TAG')
                                        if fishPopulation[k].tagged == 1:
                                            recapturedTaggedFish += 1
                                            fishPopulation[k].SetRecaughtStat('YES')
            # End Second Capture Pass

            # Estimation formula
            estimatedSampleSizeN = (((firstPassMarkedFishes + 1) * (secondPassFishes + 1)) / (recapturedTaggedFish + 1))
            simulationResult.append(estimatedSampleSizeN)
            # ######## START RAW DATA SAVING, ALLOWS USER TO VIEW RESULTS OF EACH SIMULATION ######################### #
            # Put this test result in a list for raw  data viewing:
            global testResultsArray
            if i == 0:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes, recapturedTaggedFish, fishPopulation)
                testResultsArray = [testResult]
            else:
                testResult = TestResults(populationSize, estimatedSampleSizeN, firstPassMarkedFishes, secondPassFishes, recapturedTaggedFish, fishPopulation)
                testResultsArray.insert(i, testResult)


#################################################################################
# MAIN FUNCTION
#################################################################################
if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    # setup stylesheet
    app = QApplication([])
    ui = MainWindow()
    # Set custom stylesheet:
    sys.exit(app.exec_())
