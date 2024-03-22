import Result
import os, sys
import numpy as np
import pandas as pd
from datetime import datetime

class Analyzer:

    def __init__(self):
        self.fResult = Result.Result()

    def getMetaData(self,metadata):
        print("This is a MaPSA")

    def getResult(self):
        return self.fResult

    def getRecentFile(self, filestring, name):

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

                dateString = f.split(name)[-1][1:20]
                datetimeObject = datetime.strptime(dateString, '%Y_%m_%d_%H_%M_%S')

                if datetimeObject > datetimeLatest:
                    latestFileIndex = j 
            return files[latestFileIndex]

    def analyze(self, testDir, moduleName):

        self.fResult.updateResult([moduleName],{})
        print(self.fResult)

        logfilesAllChips = []

        NAbnormalCurrent = 0
        NUnmaskable = 0
        NNonOperational = 0
        NNonOperationalPerChip = ""

        for i in range(1,17):

            chipName = str(i)
            chipSearchString = moduleName + "_" + str(i)

            print(chipName)
            logfile = self.getRecentFile(testDir + '/log*_' + chipSearchString + '_*.log', chipSearchString)
            logfilesAllChips += [logfile]

            # Current draw
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Ianalog','P_ana'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Idigital','P_dig'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Ipad','P_pad'))
            self.fResult.updateResult([moduleName,chipName],self.getCurrent(logfile,'Itotal','Total: '))
            
            itotal = 200 #self.fResult.getResultValue([moduleName,chipName,'Itotal']) 
            if itotal > 250 or itotal < 150:
                NAbnormalCurrent += 1

            # Pixel alive
            # number and list of dead, ineffient, noisy
            pafile = self.getRecentFile(testDir + '/mpa_test_'+ chipSearchString + '_*_pixelalive.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Dead'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Inefficient'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(pafile,'Noisy'))

            # Mask
            maskfile = self.getRecentFile(testDir + '/mpa_test_' + chipSearchString + '_*_mask_test.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(maskfile,'Unmaskable'))
            NUnmaskable += self.fResult.getResultValue([moduleName,chipName,'NUnmaskablePix'])

            # Noise and Pedestal
            noisefile = self.getRecentFile(testDir + '/mpa_test_' + chipSearchString + '_*_PostTrim_CAL_CAL_RMS.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(noisefile,'Noise'))

            pedestalfile = self.getRecentFile(testDir + '/mpa_test_' + chipSearchString + '_*_PostTrim_CAL_CAL_Mean.csv', chipSearchString)
            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(pedestalfile,'Pedestal'))

            # Bad bumps
            # number and list of bad bumps
            
            nonOperational = []
            for variable in ['DeadPix','InefficientPix','NoisyPix']: # Add untrimmable and bad bump
                nonOperational += self.fResult.getResultValue([moduleName,chipName,variable]).split(',')[:-1]
            
            nonOperational = np.unique(nonOperational)
            self.fResult.updateResult([moduleName,chipName],dict({'NNonOperational':len(nonOperational)}))
            NNonOperational += len(nonOperational)
            NNonOperationalPerChip += str(len(nonOperational))+','

        self.fResult.updateResult([moduleName,'NAbnormalCurrentChips'],NAbnormalCurrent)
        self.fResult.updateResult([moduleName,'NUnmaskablePix'],NUnmaskable)
        self.fResult.updateResult([moduleName,'NNonOperationalPix'],NNonOperational)
        self.fResult.updateResult([moduleName,'NNonOperationalPixPerChip'],NNonOperationalPerChip)

#        IVData = self.getIVScan(testDir + '/IVScan_'+moduleName+'.csv')
#        self.fResult.updateResult([moduleName,'Iat600V'],np.array(IVData[IVData['V']==-600]['I'])[0])

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

        elif varname == "Noisy":
            indices = np.where((data>100))[0]

        elif varname == "Unmaskable":
            indices = np.where(data > 0)[0]

        pixelString = ""
        for i in indices:
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
        returnDict[varname+"NOutliersHigh"] = len(outliersHigh)
        returnDict[varname+"OutliersHigh"] = outliersHighString

        return returnDict
        
    # Extract useful info about the IV scan
    def getIVScan(self, IVFile):

        return pd.read_csv(IVFile,delimiter='\t',header=None,names=['V','I'])

