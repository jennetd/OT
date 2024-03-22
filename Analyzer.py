import Result
from CollectMaPSAs import MaPSA
import pickle
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

    def analyze(self, moduleName):

        self.fResult.updateResult([moduleName],{})
        
        fname = 'pickles/'+moduleName+'.pkl'
        if os.path.isfile(fname):
            print("Loading MaPSA " + moduleName)
            mapsafile = open(fname, 'rb')
            mapsa = pickle.load(mapsafile)
            mapsafile.close()

        NAbnormalCurrent = 0
        NUnmaskable = 0
        NNonOperational = 0

        mpa_grades = []
 
        for chip in mapsa.mpa_chips:

            chipName = chip.index

            self.fResult.updateResult([moduleName,chipName],{'serial_number':chip.serial_number})

            # Current analysis
            self.fResult.updateResult([moduleName,chipName],{'I_ana':chip.I_ana})
            self.fResult.updateResult([moduleName,chipName],{'I_dig':chip.I_dig})
            self.fResult.updateResult([moduleName,chipName],{'I_pad':chip.I_pad})
            self.fResult.updateResult([moduleName,chipName],{'I_tot':chip.I_tot})
            
            itotal = chip.I_tot
            if itotal > 250 or itotal < 150:
                NAbnormalCurrent += 1
                Itot_Grade = 'C'
            else:
                Itot_Grade = 'A'

            # Pixel analysis
            chipdata = chip.pixels
                            
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(chipdata,'Dead'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(chipdata,'Inefficient'))
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(chipdata,'Noisy'))

            # Mask
            self.fResult.updateResult([moduleName,chipName],self.getNumberAndList(chipdata,'Unmaskable'))
            NUnmaskable += self.fResult.getResultValue([moduleName,chipName,'NUnmaskablePix'])

            # Noise and Pedestal
#            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(chipdata,'Noise'))
#            self.fResult.updateResult([moduleName,chipName],self.getMeanStdOutliers(chipdata,'Pedestal'))

            # Bad bumps
            # number and list of bad bumps
            
            nonOperational = []
            for variable in ['DeadPix','InefficientPix','NoisyPix']: # Add untrimmable and bad bump
                nonOperational += self.fResult.getResultValue([moduleName,chipName,variable]).split(',')[:-1]
            
            nonOperational = np.unique(nonOperational)
            self.fResult.updateResult([moduleName,chipName,'NNonOperational'],len(nonOperational))
            NNonOperational += len(nonOperational)

            if len(nonOperational) < 19:
                Pix_Grade = 'A'
            elif len(nonOperational) >= 19 and len(nonOperational) <= 94:
                Pix_Grade = 'B'
            elif len(nonOperational) > 94:
                Pix_Grade = 'C'
                
            # Any unmaskable = grade C
            if self.fResult.getResultValue([moduleName,chipName,'NUnmaskablePix']) !=0:
                Pix_Grade = 'C'

            MPA_Grade = max(Itot_Grade,Pix_Grade)
            mpa_grades += [MPA_Grade]

#            print("MPA " +str(chipName)+ " Grade",MPA_Grade)

            # Set the grades
            self.fResult.updateResult([moduleName,chipName],{'Itot_Grade':Itot_Grade,'Pix_Grade':Pix_Grade,'MPA_Grade':MPA_Grade})


        self.fResult.updateResult([moduleName,'kapton'],mapsa.kapton)
        self.fResult.updateResult([moduleName,'NAbnormalCurrent'],NAbnormalCurrent)
        self.fResult.updateResult([moduleName,'NUnmaskablePix'],NUnmaskable)
        self.fResult.updateResult([moduleName,'NNonOperationalPix'],NNonOperational)
        
        IVData = mapsa.IV.astype(float)
        at800 = IVData[abs(IVData['V']) == 800.0]
        Iat800 = abs(at800['I'].iloc[0])

        if Iat800 > 10.0:
           IV_Grade = 'C'
        elif Iat800 > 1.0:
           IV_Grade = 'B'
        else:
           IV_Grade = 'A'
        self.fResult.updateResult([moduleName,'IV_Grade'],IV_Grade)

        # Rework candidate?
        C_counts = mpa_grades.count('C')
        
        if C_counts in (1,2,3) and IV_Grade == 'A':
            self.fResult.updateResult([moduleName,'Rework'],'Yes')
        else:
            self.fResult.updateResult([moduleName,'Rework'],'No')
            
        MaPSA_Grade = max(max(mpa_grades), IV_Grade)
        self.fResult.updateResult([moduleName,'Total_Grade'],MaPSA_Grade)

        print('Total MaPSA Grade', MaPSA_Grade)

    # Description
    def getNumberAndList(self, data, varname, threshold=5):
        returnDict = {}

        if varname == 'Dead':
            indices = np.where(data['pa']==0)[0]
            
        elif varname == "Inefficient":
            indices = np.where((data['pa']<100) & (data['pa']>0))[0]

        elif varname == "Noisy":
            indices = np.where((data['pa']>300))[0]

        elif varname == "Unmaskable":
            indices = np.where(data['mask'] > 0)[0]

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
        
