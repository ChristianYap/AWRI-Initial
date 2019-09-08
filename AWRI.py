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
        self.setupUi(self)
        self.Connections()
        self.show()

    #################################################################################
    # Connections for the buttons
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
    # SIMULATION - TAB TWO
    #################################################################################
    def simulateFishes(self):
        QMessageBox.information(self, "A Good Message", "Success. Results shown in the results box.")
        np.random.seed(100)
        np_hist = np.random.normal(loc=0, scale=1, size=1000)
        np_hist[:10]
        hist, bin_edges = np.histogram(np_hist)
        plt.figure(figsize=[10, 8])
        plt.bar(bin_edges[:-1], hist, width=0.5, color='#0504aa', alpha=0.7)
        plt.xlim(min(bin_edges), max(bin_edges))
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value', fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Frequency', fontsize=15)
        plt.title('Normal Distribution Histogram', fontsize=15)
        plt.show()

        #https://www.datacamp.com/community/tutorials/histograms-matplotlib



#################################################################################
# MAIN FUNCTION
#################################################################################
if __name__ == "__main__":
    app = QApplication([])
    ui = MainWindow()
    sys.exit(app.exec_())
