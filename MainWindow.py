# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AWRI-GUI.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(965, 742)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabBox = QtWidgets.QTabWidget(self.centralwidget)
        self.tabBox.setObjectName("tabBox")
        self.tabEstimator = QtWidgets.QWidget()
        self.tabEstimator.setObjectName("tabEstimator")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tabEstimator)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.estimatePopulationButton = QtWidgets.QPushButton(self.tabEstimator)
        self.estimatePopulationButton.setObjectName("estimatePopulationButton")
        self.gridLayout_2.addWidget(self.estimatePopulationButton, 5, 3, 1, 2)
        self.markedSecondCatchInput = QtWidgets.QSpinBox(self.tabEstimator)
        self.markedSecondCatchInput.setMinimum(0)
        self.markedSecondCatchInput.setMaximum(1000000)
        self.markedSecondCatchInput.setProperty("value", 0)
        self.markedSecondCatchInput.setObjectName("markedSecondCatchInput")
        self.gridLayout_2.addWidget(self.markedSecondCatchInput, 2, 4, 1, 1)
        self.titleFirstTab = QtWidgets.QLabel(self.tabEstimator)
        self.titleFirstTab.setAutoFillBackground(False)
        self.titleFirstTab.setObjectName("titleFirstTab")
        self.gridLayout_2.addWidget(self.titleFirstTab, 0, 0, 1, 2)
        self.resultScreenOne = QtWidgets.QTextEdit(self.tabEstimator)
        self.resultScreenOne.setObjectName("resultScreenOne")
        self.gridLayout_2.addWidget(self.resultScreenOne, 4, 0, 1, 5)
        self.resultTitle = QtWidgets.QLabel(self.tabEstimator)
        self.resultTitle.setObjectName("resultTitle")
        self.gridLayout_2.addWidget(self.resultTitle, 3, 0, 1, 1)
        self.clearResultsScreenButton = QtWidgets.QPushButton(self.tabEstimator)
        self.clearResultsScreenButton.setObjectName("clearResultsScreenButton")
        self.gridLayout_2.addWidget(self.clearResultsScreenButton, 5, 2, 1, 1)
        self.markedFirstCatchInput = QtWidgets.QSpinBox(self.tabEstimator)
        self.markedFirstCatchInput.setMinimum(1)
        self.markedFirstCatchInput.setMaximum(1000000)
        self.markedFirstCatchInput.setProperty("value", 1)
        self.markedFirstCatchInput.setObjectName("markedFirstCatchInput")
        self.gridLayout_2.addWidget(self.markedFirstCatchInput, 1, 1, 2, 1)
        self.markedFirstCatchTitle = QtWidgets.QLabel(self.tabEstimator)
        self.markedFirstCatchTitle.setObjectName("markedFirstCatchTitle")
        self.gridLayout_2.addWidget(self.markedFirstCatchTitle, 1, 0, 2, 1)
        self.caughtSecondCatchInput = QtWidgets.QSpinBox(self.tabEstimator)
        self.caughtSecondCatchInput.setMinimum(0)
        self.caughtSecondCatchInput.setMaximum(1000000)
        self.caughtSecondCatchInput.setProperty("value", 0)
        self.caughtSecondCatchInput.setObjectName("caughtSecondCatchInput")
        self.gridLayout_2.addWidget(self.caughtSecondCatchInput, 0, 4, 2, 1)
        self.markedSecondCatchTitle = QtWidgets.QLabel(self.tabEstimator)
        self.markedSecondCatchTitle.setObjectName("markedSecondCatchTitle")
        self.gridLayout_2.addWidget(self.markedSecondCatchTitle, 2, 3, 1, 1)
        self.caughtSecondCatchTitle = QtWidgets.QLabel(self.tabEstimator)
        self.caughtSecondCatchTitle.setObjectName("caughtSecondCatchTitle")
        self.gridLayout_2.addWidget(self.caughtSecondCatchTitle, 0, 3, 2, 1)
        self.tabBox.addTab(self.tabEstimator, "")
        self.tabSimulator = QtWidgets.QWidget()
        self.tabSimulator.setObjectName("tabSimulator")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tabSimulator)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.tagLossProbabilityInput = QtWidgets.QDoubleSpinBox(self.tabSimulator)
        self.tagLossProbabilityInput.setEnabled(False)
        self.tagLossProbabilityInput.setMaximum(1.0)
        self.tagLossProbabilityInput.setSingleStep(0.01)
        self.tagLossProbabilityInput.setObjectName("tagLossProbabilityInput")
        self.gridLayout_4.addWidget(self.tagLossProbabilityInput, 4, 1, 1, 1)
        self.migrationRateSlider = QtWidgets.QSlider(self.tabSimulator)
        self.migrationRateSlider.setToolTipDuration(-1)
        self.migrationRateSlider.setWhatsThis("")
        self.migrationRateSlider.setMaximum(100)
        self.migrationRateSlider.setProperty("value", 50)
        self.migrationRateSlider.setSliderPosition(50)
        self.migrationRateSlider.setOrientation(QtCore.Qt.Horizontal)
        self.migrationRateSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.migrationRateSlider.setTickInterval(1)
        self.migrationRateSlider.setObjectName("migrationRateSlider")
        self.gridLayout_4.addWidget(self.migrationRateSlider, 1, 4, 1, 2)
        self.captureProbabilityTitle = QtWidgets.QLabel(self.tabSimulator)
        self.captureProbabilityTitle.setObjectName("captureProbabilityTitle")
        self.gridLayout_4.addWidget(self.captureProbabilityTitle, 2, 0, 1, 1)
        self.checkBoxTagLoss = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxTagLoss.setChecked(False)
        self.checkBoxTagLoss.setObjectName("checkBoxTagLoss")
        self.gridLayout_4.addWidget(self.checkBoxTagLoss, 4, 3, 1, 2)
        self.numTrialsInput = QtWidgets.QSpinBox(self.tabSimulator)
        self.numTrialsInput.setMinimum(1)
        self.numTrialsInput.setMaximum(1000000)
        self.numTrialsInput.setProperty("value", 1)
        self.numTrialsInput.setObjectName("numTrialsInput")
        self.gridLayout_4.addWidget(self.numTrialsInput, 6, 4, 1, 1)
        self.checkBoxCaptureEqual = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxCaptureEqual.setChecked(True)
        self.checkBoxCaptureEqual.setObjectName("checkBoxCaptureEqual")
        self.gridLayout_4.addWidget(self.checkBoxCaptureEqual, 2, 3, 1, 2)
        self.tagLossTitle = QtWidgets.QLabel(self.tabSimulator)
        self.tagLossTitle.setObjectName("tagLossTitle")
        self.gridLayout_4.addWidget(self.tagLossTitle, 4, 0, 1, 1)
        self.checkBoxNoSubreach = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxNoSubreach.setWhatsThis("")
        self.checkBoxNoSubreach.setChecked(True)
        self.checkBoxNoSubreach.setTristate(False)
        self.checkBoxNoSubreach.setObjectName("checkBoxNoSubreach")
        self.gridLayout_4.addWidget(self.checkBoxNoSubreach, 5, 1, 1, 2)
        self.checkBoxExpandedSubreach = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxExpandedSubreach.setChecked(False)
        self.checkBoxExpandedSubreach.setTristate(False)
        self.checkBoxExpandedSubreach.setObjectName("checkBoxExpandedSubreach")
        self.gridLayout_4.addWidget(self.checkBoxExpandedSubreach, 5, 5, 1, 1)
        self.checkBoxClosedPopulation = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxClosedPopulation.setToolTipDuration(-1)
        self.checkBoxClosedPopulation.setWhatsThis("")
        self.checkBoxClosedPopulation.setAccessibleName("")
        self.checkBoxClosedPopulation.setAccessibleDescription("")
        self.checkBoxClosedPopulation.setChecked(True)
        self.checkBoxClosedPopulation.setTristate(False)
        self.checkBoxClosedPopulation.setObjectName("checkBoxClosedPopulation")
        self.gridLayout_4.addWidget(self.checkBoxClosedPopulation, 0, 3, 1, 2)
        self.mortalityProbabilityTitle = QtWidgets.QLabel(self.tabSimulator)
        self.mortalityProbabilityTitle.setObjectName("mortalityProbabilityTitle")
        self.gridLayout_4.addWidget(self.mortalityProbabilityTitle, 1, 0, 1, 1)
        self.subReachMovementOption = QtWidgets.QRadioButton(self.tabSimulator)
        self.subReachMovementOption.setEnabled(False)
        self.subReachMovementOption.setObjectName("subReachMovementOption")
        self.gridLayout_4.addWidget(self.subReachMovementOption, 5, 6, 1, 1)
        self.runSimulationButton = QtWidgets.QPushButton(self.tabSimulator)
        self.runSimulationButton.setObjectName("runSimulationButton")
        self.gridLayout_4.addWidget(self.runSimulationButton, 6, 6, 1, 1)
        self.totalPopulationInput = QtWidgets.QSpinBox(self.tabSimulator)
        self.totalPopulationInput.setMinimum(1)
        self.totalPopulationInput.setMaximum(1000000)
        self.totalPopulationInput.setProperty("value", 1)
        self.totalPopulationInput.setObjectName("totalPopulationInput")
        self.gridLayout_4.addWidget(self.totalPopulationInput, 0, 1, 1, 1)
        self.numTrialsTitle = QtWidgets.QLabel(self.tabSimulator)
        self.numTrialsTitle.setObjectName("numTrialsTitle")
        self.gridLayout_4.addWidget(self.numTrialsTitle, 6, 3, 1, 1)
        self.checkBoxOpenPopulation = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxOpenPopulation.setObjectName("checkBoxOpenPopulation")
        self.gridLayout_4.addWidget(self.checkBoxOpenPopulation, 0, 5, 1, 1)
        self.subReachSizeTitle = QtWidgets.QLabel(self.tabSimulator)
        self.subReachSizeTitle.setObjectName("subReachSizeTitle")
        self.gridLayout_4.addWidget(self.subReachSizeTitle, 5, 0, 1, 1)
        self.totalPopulationTitle = QtWidgets.QLabel(self.tabSimulator)
        self.totalPopulationTitle.setObjectName("totalPopulationTitle")
        self.gridLayout_4.addWidget(self.totalPopulationTitle, 0, 0, 1, 1)
        self.stopSimulationButton = QtWidgets.QPushButton(self.tabSimulator)
        self.stopSimulationButton.setEnabled(False)
        self.stopSimulationButton.setObjectName("stopSimulationButton")
        self.gridLayout_4.addWidget(self.stopSimulationButton, 6, 5, 1, 1)
        self.captureProbabilityInputVaryTwo = QtWidgets.QDoubleSpinBox(self.tabSimulator)
        self.captureProbabilityInputVaryTwo.setEnabled(False)
        self.captureProbabilityInputVaryTwo.setMaximum(1.0)
        self.captureProbabilityInputVaryTwo.setSingleStep(0.01)
        self.captureProbabilityInputVaryTwo.setObjectName("captureProbabilityInputVaryTwo")
        self.gridLayout_4.addWidget(self.captureProbabilityInputVaryTwo, 3, 1, 1, 1)
        self.openPopulationMoralityInput = QtWidgets.QDoubleSpinBox(self.tabSimulator)
        self.openPopulationMoralityInput.setEnabled(True)
        self.openPopulationMoralityInput.setMaximum(1.0)
        self.openPopulationMoralityInput.setSingleStep(0.01)
        self.openPopulationMoralityInput.setObjectName("openPopulationMoralityInput")
        self.gridLayout_4.addWidget(self.openPopulationMoralityInput, 1, 1, 1, 1)
        self.checkBoxCaptureVary = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxCaptureVary.setObjectName("checkBoxCaptureVary")
        self.gridLayout_4.addWidget(self.checkBoxCaptureVary, 2, 5, 1, 1)
        self.checkBoxCaptureRandomPerFish = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxCaptureRandomPerFish.setObjectName("checkBoxCaptureRandomPerFish")
        self.gridLayout_4.addWidget(self.checkBoxCaptureRandomPerFish, 3, 3, 1, 4)
        self.checkBoxNormalSubreach = QtWidgets.QCheckBox(self.tabSimulator)
        self.checkBoxNormalSubreach.setChecked(False)
        self.checkBoxNormalSubreach.setTristate(False)
        self.checkBoxNormalSubreach.setObjectName("checkBoxNormalSubreach")
        self.gridLayout_4.addWidget(self.checkBoxNormalSubreach, 5, 3, 1, 2)
        self.captureProbabilityInput = QtWidgets.QDoubleSpinBox(self.tabSimulator)
        self.captureProbabilityInput.setStatusTip("")
        self.captureProbabilityInput.setMaximum(1.0)
        self.captureProbabilityInput.setSingleStep(0.01)
        self.captureProbabilityInput.setObjectName("captureProbabilityInput")
        self.gridLayout_4.addWidget(self.captureProbabilityInput, 2, 1, 1, 1)
        self.migrationRateTitle = QtWidgets.QLabel(self.tabSimulator)
        self.migrationRateTitle.setObjectName("migrationRateTitle")
        self.gridLayout_4.addWidget(self.migrationRateTitle, 1, 3, 1, 1)
        self.migrationRateBox = QtWidgets.QDoubleSpinBox(self.tabSimulator)
        self.migrationRateBox.setEnabled(False)
        self.migrationRateBox.setMaximum(1.0)
        self.migrationRateBox.setSingleStep(0.01)
        self.migrationRateBox.setProperty("value", 0.5)
        self.migrationRateBox.setObjectName("migrationRateBox")
        self.gridLayout_4.addWidget(self.migrationRateBox, 1, 6, 1, 1)
        self.tabBox.addTab(self.tabSimulator, "")
        self.tabResults = QtWidgets.QWidget()
        self.tabResults.setObjectName("tabResults")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tabResults)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.loadSimulationNumberInput = QtWidgets.QComboBox(self.tabResults)
        self.loadSimulationNumberInput.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadSimulationNumberInput.setAutoFillBackground(False)
        self.loadSimulationNumberInput.setEditable(True)
        self.loadSimulationNumberInput.setCurrentText("")
        self.loadSimulationNumberInput.setMaxCount(29)
        self.loadSimulationNumberInput.setMinimumContentsLength(1)
        self.loadSimulationNumberInput.setObjectName("loadSimulationNumberInput")
        self.gridLayout_3.addWidget(self.loadSimulationNumberInput, 1, 1, 1, 1)
        self.simulationReviewer = QtWidgets.QTextEdit(self.tabResults)
        self.simulationReviewer.setObjectName("simulationReviewer")
        self.gridLayout_3.addWidget(self.simulationReviewer, 2, 0, 1, 2)
        self.refreshResultsButton = QtWidgets.QPushButton(self.tabResults)
        self.refreshResultsButton.setEnabled(False)
        self.refreshResultsButton.setObjectName("refreshResultsButton")
        self.gridLayout_3.addWidget(self.refreshResultsButton, 1, 2, 1, 1)
        self.tableRawFishData = QtWidgets.QTableWidget(self.tabResults)
        self.tableRawFishData.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableRawFishData.setAlternatingRowColors(True)
        self.tableRawFishData.setObjectName("tableRawFishData")
        self.tableRawFishData.setColumnCount(9)
        self.tableRawFishData.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawFishData.setHorizontalHeaderItem(8, item)
        self.gridLayout_3.addWidget(self.tableRawFishData, 2, 2, 3, 4)
        self.simulationParameterPrint = QtWidgets.QTextEdit(self.tabResults)
        self.simulationParameterPrint.setObjectName("simulationParameterPrint")
        self.gridLayout_3.addWidget(self.simulationParameterPrint, 0, 0, 1, 6)
        self.trialsLabel = QtWidgets.QLabel(self.tabResults)
        self.trialsLabel.setObjectName("trialsLabel")
        self.gridLayout_3.addWidget(self.trialsLabel, 3, 0, 1, 1)
        self.tableRawTestData = QtWidgets.QTableWidget(self.tabResults)
        self.tableRawTestData.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableRawTestData.setAlternatingRowColors(True)
        self.tableRawTestData.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableRawTestData.setObjectName("tableRawTestData")
        self.tableRawTestData.setColumnCount(4)
        self.tableRawTestData.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawTestData.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawTestData.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawTestData.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRawTestData.setHorizontalHeaderItem(3, item)
        self.gridLayout_3.addWidget(self.tableRawTestData, 4, 0, 1, 2)
        self.rawDataTableLabel = QtWidgets.QLabel(self.tabResults)
        self.rawDataTableLabel.setObjectName("rawDataTableLabel")
        self.gridLayout_3.addWidget(self.rawDataTableLabel, 1, 0, 1, 1)
        self.viewImageButton = QtWidgets.QPushButton(self.tabResults)
        self.viewImageButton.setEnabled(False)
        self.viewImageButton.setObjectName("viewImageButton")
        self.gridLayout_3.addWidget(self.viewImageButton, 1, 3, 1, 1)
        self.clearDataButton = QtWidgets.QPushButton(self.tabResults)
        self.clearDataButton.setEnabled(False)
        self.clearDataButton.setObjectName("clearDataButton")
        self.gridLayout_3.addWidget(self.clearDataButton, 1, 5, 1, 1)
        self.tabBox.addTab(self.tabResults, "")
        self.gridLayout.addWidget(self.tabBox, 0, 0, 1, 1)
        self.saveResultsButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveResultsButton.setObjectName("saveResultsButton")
        self.gridLayout.addWidget(self.saveResultsButton, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 965, 21))
        self.menubar.setObjectName("menubar")
        self.menuMain = QtWidgets.QMenu(self.menubar)
        self.menuMain.setObjectName("menuMain")
        self.menuResults = QtWidgets.QMenu(self.menubar)
        self.menuResults.setObjectName("menuResults")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuMain.menuAction())
        self.menubar.addAction(self.menuResults.menuAction())

        self.retranslateUi(MainWindow)
        self.tabBox.setCurrentIndex(2)
        self.loadSimulationNumberInput.setCurrentIndex(-1)
        self.clearResultsScreenButton.clicked.connect(self.resultScreenOne.clear)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AWRI | Mark Recapture Population Estimator v1.2019"))
        self.estimatePopulationButton.setText(_translate("MainWindow", "Estimate Population"))
        self.titleFirstTab.setText(_translate("MainWindow", "Lincoln Peterson (Chapman\'s) Estimator"))
        self.resultScreenOne.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.resultTitle.setText(_translate("MainWindow", "Results"))
        self.clearResultsScreenButton.setText(_translate("MainWindow", "Clear Results Screen"))
        self.markedFirstCatchTitle.setText(_translate("MainWindow", "# of Fishes Marked in First Catch (M):"))
        self.markedSecondCatchTitle.setText(_translate("MainWindow", "# of Fishes Marked in Second Catch (R):"))
        self.caughtSecondCatchTitle.setText(_translate("MainWindow", "# of Fishes Caught in Second Catch (N):"))
        self.tabBox.setTabText(self.tabBox.indexOf(self.tabEstimator), _translate("MainWindow", "Lincoln-Peterson (Chapman\'s) Estimator"))
        self.migrationRateSlider.setToolTip(_translate("MainWindow", "<html><head/><body><p>Change Rate of Migration. At 0, rate of fish leaving reach is highest. At 1, rate of fish entering reach is highest. At .50, rate is balanced.</p></body></html>"))
        self.migrationRateSlider.setStatusTip(_translate("MainWindow", "0 - Maximum Rate for Fish to Exit the Subreach 0.5 - Balanced Rate for Fish Entering/Exiting Subreach 1 - Maximum Rate for Fish to Enter the Subreach"))
        self.captureProbabilityTitle.setText(_translate("MainWindow", "Capture Probability:"))
        self.checkBoxTagLoss.setText(_translate("MainWindow", "Possible Tag Loss"))
        self.checkBoxCaptureEqual.setText(_translate("MainWindow", "Equal Between Samples"))
        self.tagLossTitle.setText(_translate("MainWindow", "Tag Loss Probability:"))
        self.checkBoxNoSubreach.setStatusTip(_translate("MainWindow", "All fishes are in the subreach"))
        self.checkBoxNoSubreach.setText(_translate("MainWindow", "Not a Factor"))
        self.checkBoxExpandedSubreach.setText(_translate("MainWindow", "Expanded Subreach Size"))
        self.checkBoxClosedPopulation.setToolTip(_translate("MainWindow", "Closed Population: No fish birth/death occurs between each sample taken, as well as no fishes enter or leave the sample subreach area."))
        self.checkBoxClosedPopulation.setStatusTip(_translate("MainWindow", "User must choose whether simulation will have an open or closed population."))
        self.checkBoxClosedPopulation.setText(_translate("MainWindow", "Closed Population"))
        self.mortalityProbabilityTitle.setText(_translate("MainWindow", "Mortality Probability:"))
        self.subReachMovementOption.setText(_translate("MainWindow", "Limit Subreach Movement"))
        self.runSimulationButton.setText(_translate("MainWindow", "Run Simulation"))
        self.numTrialsTitle.setText(_translate("MainWindow", "Number of Trials:"))
        self.checkBoxOpenPopulation.setText(_translate("MainWindow", "Open Population (Mortality / Migration)"))
        self.subReachSizeTitle.setText(_translate("MainWindow", "Subreach Size:"))
        self.totalPopulationTitle.setText(_translate("MainWindow", "Total Fish Population in Reach:"))
        self.stopSimulationButton.setText(_translate("MainWindow", "Stop Simulation"))
        self.checkBoxCaptureVary.setText(_translate("MainWindow", "Vary Between Samples"))
        self.checkBoxCaptureRandomPerFish.setText(_translate("MainWindow", "Randomize Probability for Each Fish"))
        self.checkBoxNormalSubreach.setWhatsThis(_translate("MainWindow", "Fishes are put in 4 zones, 2 of the zones are the only areas where fish can get caught."))
        self.checkBoxNormalSubreach.setText(_translate("MainWindow", "Normal Subreach Size"))
        self.captureProbabilityInput.setToolTip(_translate("MainWindow", "Input must be between 0 to 1, inclusve."))
        self.migrationRateTitle.setText(_translate("MainWindow", "Migration Rate:"))
        self.tabBox.setTabText(self.tabBox.indexOf(self.tabSimulator), _translate("MainWindow", "Raw Simulation"))
        self.refreshResultsButton.setText(_translate("MainWindow", "Load Data"))
        self.tableRawFishData.setSortingEnabled(True)
        item = self.tableRawFishData.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Capture Prob (Q1)"))
        item = self.tableRawFishData.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Initial Subreach (S1)"))
        item = self.tableRawFishData.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Tagged"))
        item = self.tableRawFishData.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Tag Lost"))
        item = self.tableRawFishData.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Mortality"))
        item.setToolTip(_translate("MainWindow", "1 - Fish is alive. 0 - Fish is dead."))
        item.setWhatsThis(_translate("MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        item = self.tableRawFishData.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Enter/Stay/Exit"))
        item = self.tableRawFishData.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Capture Prob (Q2)"))
        item = self.tableRawFishData.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Final Subreach (S2)"))
        item = self.tableRawFishData.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Recaught"))
        self.trialsLabel.setText(_translate("MainWindow", "Trials"))
        self.tableRawTestData.setSortingEnabled(True)
        item = self.tableRawTestData.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Est. Pop"))
        item = self.tableRawTestData.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "First Pass Catch"))
        item = self.tableRawTestData.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Second Pass Catch"))
        item = self.tableRawTestData.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Recatch"))
        self.rawDataTableLabel.setText(_translate("MainWindow", "Load Simulation Set:"))
        self.viewImageButton.setText(_translate("MainWindow", "View Image"))
        self.clearDataButton.setText(_translate("MainWindow", "Clear All Saved Data"))
        self.tabBox.setTabText(self.tabBox.indexOf(self.tabResults), _translate("MainWindow", "Results"))
        self.saveResultsButton.setText(_translate("MainWindow", "Save Results"))
        self.menuMain.setTitle(_translate("MainWindow", "File"))
        self.menuResults.setTitle(_translate("MainWindow", "Options"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
