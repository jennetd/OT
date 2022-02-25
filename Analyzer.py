import Result
import os, sys
import numpy as np
from datetime import datetime

class Analyzer:

    def __init__(self):
        self.fResult = Result.Result()

    def getMetaData(self,metadata):
        print("This is a MaPSA")

    def getResult(self):
        return self.fResult

    def getRecentFile(self, filestring, chipName):

        files = os.popen('ls '+filestring).read().split()

        if len(files) < 1:
            print("Error: no files specified")
            return "0"

        elif len(files) == 1:
            return files[0]

        else:
            latestFileIndex = -1
            datetimeLatest = datetime.strptime('2000_01_01_01_00_00', '%Y_%m_%d_%H_%M_%S')
            for j, f in enumerate(files):
                dateString = f.split(chipName)[-1][1:20]
                datetimeObject = datetime.strptime(dateString, '%Y_%m_%d_%H_%M_%S')

                if datetimeObject > datetimeLatest:
                    latestFileIndex = j 
            return files[latestFileIndex]

    def analyze(self, testDir, moduleName):

        self.fResult.updateResult([moduleName],{})
        print(self.fResult)

        logfilesAllChips = []

        for i in range(1,17):

            chipName = "Chip"+str(i)
            logfile = self.getRecentFile(testDir + '/log*_' + chipName + '_*.log', chipName)
            logfilesAllChips += [logfile]

            # Current draw
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Ianalog','P_ana'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Idigital','P_dig'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Ipad','P_pad'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Itotal','Total: '))

            # Pixel alive
            # number and list of dead, ineffient, noisy
            pafile = self.getRecentFile(testDir + '/mpa_test_*_'+ chipName + '_*_pixelalive.csv', chipName)
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Dead'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Inefficient'))

            # Mask
            maskfile = self.getRecentFile(testDir + '/mpa_test_*_' + chipName + '_*_mask_test.csv', chipName)
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(maskfile,'Unmaskable'))
            
            # Trim
            trimfile = self.getRecentFile(testDir + '/mpa_test_*_' + chipName + '_*_Trim_trimbits.csv', chipName)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(trimfile,'Offset'))
            # number of untrimmable

            # Noise and Pedestal
            noisefile = self.getRecentFile(testDir + '/mpa_test_*_' + chipName + '_*_PostTrim_CAL_CAL_RMS.csv', chipName)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(noisefile,'Noise'))

            pedestalfile = self.getRecentFile(testDir + '/mpa_test_*_' + chipName + '_*_PostTrim_CAL_CAL_Mean.csv', chipName)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(pedestalfile,'Pedestal'))

            # Bad bumps
            # number and list of bad bumps

    def getCurrent(self, logfile, varname, tag):
        returnDict = {}
        if len(logfile) <= 1:
            return returnDict

        cmd = "grep " + tag + " " + logfile
        x = os.popen(cmd).read()
        x = x.replace('I= ', 'CUT')
        x = x.replace(' mA', 'CUT')
        y = x.split('CUT')
        I = float(y[1])

        # Add it to the dict
        returnDict[varname] = I
        return returnDict
        
    # Description
    def getNumberAndList(self, datafile, varname, threshold=5):
        returnDict = {}

        if len(datafile) <= 1:
            return returnDict

        data = np.genfromtxt(datafile, delimiter=',')[:,1][1:]

        if varname == 'Dead':
            indices = np.where(data==0)[0]
            
        elif varname == "Inefficient":
            indices = np.where((data<100) & (data>0))[0]

        elif varname == "Unmaskable":
            indices = np.where(data > 0)[0]

        pixelString = ""
        for i in indices:
            print(i)
            pixelString += str(i)+","

        returnDict["N"+varname+"Pix"] = len(indices)
        returnDict[varname+"Pix"] = pixelString

        return returnDict
        
    # Extract useful info about noise given the part name and hist of noise / channel
    def getMeanStdOutliers(self, datafile, varname, threshold=5):
        # threshold = number of sigma away from mean that qualifies as "outlier"
        returnDict = {}

        if len(datafile) <= 1:
            return returnDict

        data = np.genfromtxt(datafile, delimiter=',', dtype='float')[:,1][1:]

        mean = np.mean(data)
        std  = np.std(data)

        returnDict[varname+"Mean"] = mean
        returnDict[varname+"Std"] = std
        
        # calculate outliers                                                                                                            
        outliersHigh = []
        outliersLow = []
        for i, d in enumerate(data):
            if d > mean + threshold * std:
                outliersHigh.append(i)
            if d < mean - threshold * std:
                outliersLow.append(i)

        outliersLowString = ""
        for strip in outliersLow:
            outliersLowString += str(strip)+","
        returnDict[varname+"NOutliersLow"] = len(outliersLow)
        returnDict[varname+"OutliersLow"] = outliersLowString

        outliersHighString = ""
        for strip in outliersHigh:
            outliersHighString += str(strip)+","
        returnDict[varname+"NOutliersHigh"+varname] = len(outliersHigh)
        returnDict[varname+"OutliersHigh"+varname] = outliersHighString

        return returnDict
        
    # Extract useful info about the IV scan
    def getIVScan(self, inputObject):
        # do something
        # edit the result
        #self.fResult["breakdown"] = function on inputObject
        return

